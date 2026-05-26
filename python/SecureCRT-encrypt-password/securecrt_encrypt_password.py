"""SecureCRT 会话密码批量提取与解密工具。

主要职责：
    1. 扫描 SecureCRT 的 Sessions 目录下所有 .ini 会话文件；
    2. 从中提取 Username / Password / Password V2 字段；
    3. 调用 securecrt_cipher 中的 V1 / V2 解密器还原明文；
    4. 将结果汇总写入 CSV，包含状态与备注列，便于下游分析。

使用示例：
    # 交互式（推荐）
    python securecrt_password_extractor.py

    # 指定 Sessions 目录与输出路径
    python securecrt_password_extractor.py \
        --sessions-dir "%APPDATA%\\VanDyke\\Config\\Sessions" \
        -o passwords.csv

打包成 exe 双击运行时会自动启用 --pause，避免窗口闪退。
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from typing import Any, Optional, Tuple

# 与本文件同目录的 securecrt_cipher.py 是必需依赖。
# 目录名含连字符，无法作为 package；这里显式把脚本目录加入 sys.path，
# 保证以脚本/exe/被外部 import 等任意方式启动时都能正确解析依赖。
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from securecrt_cipher import SecureCRTCrypto, SecureCRTCryptoV2  # noqa: E402  # pyright: ignore[reportImplicitRelativeImport]


# ============================================================
# 常量定义
# ============================================================

# CSV 表头与默认输出文件名
CSV_HEADERS = ["目录层级", "文件名", "用户名", "明文密码", "密码版本", "状态", "备注"]
DEFAULT_OUTPUT_FILENAME = "securecrt_passwords.csv"

# 解密结果状态码
STATUS_SUCCESS = "success"          # 成功解密
STATUS_FAILED = "failed"            # 解密或处理失败
STATUS_NO_PASSWORD = "no_password"  # 仅有用户名、无密码字段

# 密码版本标识
VERSION_V1 = "V1"
VERSION_V2 = "V2"

# SecureCRT INI 字段正则（编译一次，全局复用）
# - V2 密码： S:"Password V2"=<prefix>:<hex>
# - V1 密码： S:"Password"=u<hex>
# - 用户名 ： S:"Username"=[hex长度 ]<value>，兼容文件末尾无换行
RE_PASSWORD_V2 = re.compile(r'S:"Password V2"\s*=\s*(\w+):([0-9a-fA-F]+)')
RE_PASSWORD_V1 = re.compile(r'S:"Password"\s*=\s*u([0-9a-fA-F]+)')
RE_USERNAME = re.compile(r'S:"Username"\s*=\s*(?:[0-9a-fA-F]{1,8}\s+)?([^\r\n]*)')

# SecureCRT Sessions 目录在 Windows 下的默认路径
DEFAULT_VANDYKE_SUBPATH = os.path.join("VanDyke", "Config", "Sessions")


# ============================================================
# INI 文件读取与字段解析
# ============================================================

def _read_ini_text(file_path: str) -> Optional[str]:
    """读取 INI 文件文本内容，通过二进制模式 + BOM 检测确定编码。

    SecureCRT 会话文件存在以下编码变体：
      - UTF-16 LE with BOM（前两字节 FF FE）
      - UTF-16 LE without BOM（无前缀，最常见）
      - UTF-8 with BOM（前三字节 EF BB BF）
      - UTF-8 without BOM（少数旧版本/手工修改文件）

    使用二进制模式读取并手动检测 BOM，比 open(encoding=...) 的隐式 BOM 检测更可靠，
    彻底避免 "UTF-16 stream does not start with BOM" 异常。

    Returns:
        文件文本内容；读取/解码失败时返回 None。
    """
    try:
        with open(file_path, "rb") as f:
            raw = f.read()
    except OSError as exc:
        print(f"读取文件失败 {file_path}: {exc}")
        return None

    if not raw:
        return ""

    # BOM 检测：优先按 BOM 确定编码
    if raw[:2] == b'\xff\xfe':
        # UTF-16 LE with BOM
        try:
            return raw.decode('utf-16-le')
        except UnicodeDecodeError:
            pass
    elif raw[:2] == b'\xfe\xff':
        # UTF-16 BE with BOM
        try:
            return raw.decode('utf-16-be')
        except UnicodeDecodeError:
            pass
    elif raw[:3] == b'\xef\xbb\xbf':
        # UTF-8 with BOM
        try:
            return raw[3:].decode('utf-8')
        except UnicodeDecodeError:
            pass

    # 无 BOM：SecureCRT 以 UTF-16 LE 为主，优先尝试
    for encoding in ('utf-16-le', 'utf-8'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    print(f"读取文件失败 {file_path}: 无法识别编码")
    return None


def extract_password_info(file_path: str) -> Optional[dict[str, Any]]:
    """从单个 INI 文件中提取用户名与密码密文信息。

    Args:
        file_path: 会话 INI 文件的绝对/相对路径。

    Returns:
        若文件包含密码或用户名，返回字典：
            {
                'version'       : 'V1' | 'V2' | None,
                'ciphertext'    : <hex 密文> 或 None,
                'prefix'        : <V2 前缀，仅 V2 存在>,
                'username'      : <用户名>,
                'v1_ciphertext' : <V1 后备密文，仅 V2 时可能存在>,
            }
        否则返回 None。
    """
    content = _read_ini_text(file_path)
    if content is None:
        return None

    # 用户名：去除可能的 hex 长度前缀与首尾空白
    username_match = RE_USERNAME.search(content)
    username = username_match.group(1).strip() if username_match else ""

    # 同时提取 V2 与 V1，便于 V2 解密失败时回退到 V1
    v2_match = RE_PASSWORD_V2.search(content)
    v1_match = RE_PASSWORD_V1.search(content)

    if v2_match:
        return {
            "version": VERSION_V2,
            "prefix": v2_match.group(1),
            "ciphertext": v2_match.group(2),
            "username": username,
            "v1_ciphertext": v1_match.group(1) if v1_match else None,
        }

    if v1_match:
        return {
            "version": VERSION_V1,
            "ciphertext": v1_match.group(1),
            "username": username,
        }

    # 仅有用户名也保留记录，便于审计
    if username:
        return {
            "version": None,
            "ciphertext": None,
            "username": username,
        }

    return None


# ============================================================
# 密码解密
# ============================================================

# 解密结果三元组：(明文密码, 状态码, 备注)
DecryptResult = Tuple[str, str, str]


def _decrypt_with_v1(ciphertext: str) -> str:
    """使用 V1 算法解密。"""
    return SecureCRTCrypto().decrypt(ciphertext)


def _decrypt_with_v2(ciphertext: str, prefix: str, passphrase: str) -> str:
    """使用 V2 算法解密。"""
    return SecureCRTCryptoV2(passphrase).decrypt(ciphertext, prefix=prefix)


def decrypt_password(password_info: dict[str, Any], config_passphrase: str) -> DecryptResult:
    """根据 password_info 中的版本调用对应解密器。

    解密策略：
        - V2 优先；V2 失败时若同会话存在 V1 密文则尝试回退；
        - V1 直接解密；
        - 无密码字段（version 为 None）返回 no_password。

    Returns:
        (明文密码, 状态码, 备注)
    """
    version = password_info.get("version")

    if version == VERSION_V2:
        ciphertext = password_info["ciphertext"]
        prefix = password_info["prefix"]
        try:
            return _decrypt_with_v2(ciphertext, prefix, config_passphrase), STATUS_SUCCESS, ""
        except Exception as err_v2:
            # V2 解密失败：尝试 V1 后备
            v1_ciphertext = password_info.get("v1_ciphertext")
            if v1_ciphertext:
                try:
                    plaintext = _decrypt_with_v1(v1_ciphertext)
                    return plaintext, STATUS_SUCCESS, f"V2失败后回退到V1: {err_v2}"
                except Exception as err_v1:
                    return "", STATUS_FAILED, f"V2失败: {err_v2}; V1回退也失败: {err_v1}"
            return "", STATUS_FAILED, f"解密失败: {err_v2}"

    if version == VERSION_V1:
        try:
            return _decrypt_with_v1(password_info["ciphertext"]), STATUS_SUCCESS, ""
        except Exception as err:
            return "", STATUS_FAILED, f"解密失败: {err}"

    return "", STATUS_NO_PASSWORD, ""


# ============================================================
# 路径解析与命令行
# ============================================================

def _get_runtime_base_dir() -> str:
    """返回脚本/exe 所在目录（兼容 PyInstaller frozen 模式）。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resolve_sessions_dir(cli_dir: Optional[str]) -> str:
    """按优先级解析 Sessions 目录。

    优先级：
        1. 命令行 --sessions-dir 指定路径；
        2. 脚本/exe 同级目录下的 Sessions 子目录；
        3. %APPDATA%\\VanDyke\\Config\\Sessions（SecureCRT Windows 默认）。

    若以上都不存在，返回第 2 项作为默认候选（由调用方再次校验是否存在）。
    """
    if cli_dir:
        return os.path.abspath(cli_dir)

    same_level_candidate = os.path.join(_get_runtime_base_dir(), "Sessions")
    if os.path.isdir(same_level_candidate):
        return same_level_candidate

    appdata = os.environ.get("APPDATA")
    if appdata:
        vandyke_default = os.path.join(appdata, DEFAULT_VANDYKE_SUBPATH)
        if os.path.isdir(vandyke_default):
            return vandyke_default

    return same_level_candidate


def resolve_output_csv_path(cli_output: Optional[str], sessions_dir: str) -> str:
    """决定 CSV 输出路径：CLI 指定优先，否则放在 Sessions 同级目录下。"""
    if cli_output:
        return cli_output
    return os.path.join(os.path.dirname(sessions_dir), DEFAULT_OUTPUT_FILENAME)


def build_arg_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(description="SecureCRT 会话密码提取与解密工具")
    parser.add_argument(
        "--sessions-dir", dest="sessions_dir", default=None,
        help="SecureCRT Sessions 目录路径（默认：脚本/exe 同级 Sessions，"
             "其次 %%APPDATA%%/VanDyke/Config/Sessions）",
    )
    parser.add_argument(
        "-o", "--output", dest="output", default=None,
        help=f"输出 CSV 文件路径（默认：Sessions 同级目录下的 {DEFAULT_OUTPUT_FILENAME}）",
    )
    parser.add_argument(
        "-p", "--passphrase", dest="passphrase", default=None,
        help="CRT 配置密码（不推荐在命令行明文传入，仅为自动化场景提供）",
    )
    parser.add_argument(
        "--pause", dest="pause", action="store_true",
        help="结束后等待回车再退出，避免双击 exe 运行时窗口闪退",
    )
    parser.add_argument(
        "--progress-every", dest="progress_every", type=int, default=50,
        help="每处理 N 个文件打印一条进度（默认 50，设为 0 则不打印）",
    )
    return parser


def _prompt_passphrase(cli_value: Optional[str]) -> Optional[str]:
    """获取配置密码：CLI 优先，否则使用 input 明文输入。

    用户按 Ctrl+C / EOF 时返回 None 表示已取消。
    """
    if cli_value is not None:
        return cli_value
    try:
        value = input("请输入CRT配置密码（若无则直接回车）: ")
    except (EOFError, KeyboardInterrupt):
        print("\n已取消。")
        return None
    return value.strip()


def _wait_for_enter(prompt: str) -> None:
    """阻塞等待回车；忽略 EOF/Ctrl+C 不再抛出。"""
    try:
        input(prompt)
    except (EOFError, KeyboardInterrupt):
        pass


# ============================================================
# 单文件 / 批量处理
# ============================================================

def _format_dir_level(root: str, sessions_dir: str) -> str:
    """把会话子目录相对路径格式化为 'a-b-c' 形式，根目录返回 'root'。"""
    relative_path = os.path.relpath(root, sessions_dir)
    if relative_path == ".":
        return "root"
    return relative_path.replace(os.sep, "-")


def _process_single_ini(
    file_path: str,
    dir_level: str,
    filename: str,
    config_passphrase: str,
    writer,
) -> Tuple[str, str]:
    """处理单个 ini 文件并写入一行 CSV。

    Returns:
        (status, note)。status 在 success / failed / no_password / 'skipped' 中选一，
        其中 'skipped' 表示该文件无任何可提取的字段，不会写入 CSV。
    """
    password_info = extract_password_info(file_path)
    if not password_info:
        return "skipped", ""

    if password_info.get("ciphertext"):
        plaintext, status, note = decrypt_password(password_info, config_passphrase)
    else:
        plaintext, status, note = "", STATUS_NO_PASSWORD, ""

    writer.writerow([
        dir_level,
        filename,
        password_info["username"],
        plaintext,
        password_info["version"] or "",
        status,
        note,
    ])
    return status, note


def process_sessions_dir(
    sessions_dir: str,
    output_csv: str,
    config_passphrase: str,
    progress_every: int,
) -> dict[str, int]:
    """遍历 Sessions 目录、逐个解密、统一写入 CSV。

    Returns:
        统计信息字典：scanned / record / success / failed / no_password。
    """
    counters = {
        "scanned": 0,        # 扫描到的 .ini 总数
        "record": 0,         # 写入 CSV 的总行数
        "success": 0,        # 成功解密
        "failed": 0,         # 解密或处理失败
        "no_password": 0,    # 仅用户名、无密码
    }

    # utf-8-sig：Excel 直接打开识别中文
    # QUOTE_ALL：防止密码含逗号/引号/换行破坏 CSV 列
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        writer.writerow(CSV_HEADERS)

        for root, _subdirs, filenames in os.walk(sessions_dir):
            for filename in filenames:
                if not filename.endswith(".ini"):
                    continue

                file_path = os.path.join(root, filename)
                counters["scanned"] += 1
                dir_level = _format_dir_level(root, sessions_dir)

                # 单文件异常隔离：保证单个 ini 失败不会终止整批
                try:
                    status, note = _process_single_ini(
                        file_path, dir_level, filename, config_passphrase, writer,
                    )
                except Exception as exc:
                    counters["failed"] += 1
                    counters["record"] += 1
                    print(f"[异常] {file_path}: {exc}")
                    try:
                        writer.writerow([
                            dir_level, filename, "", "", "",
                            STATUS_FAILED, f"处理异常: {exc}",
                        ])
                    except Exception:
                        # 写 CSV 异常不再向上抛，避免破坏后续记录
                        pass
                else:
                    if status == "skipped":
                        # 无任何字段，不计入 record
                        continue
                    counters["record"] += 1
                    if status == STATUS_SUCCESS:
                        counters["success"] += 1
                    elif status == STATUS_FAILED:
                        counters["failed"] += 1
                        print(f"[失败] {file_path}: {note}")
                    elif status == STATUS_NO_PASSWORD:
                        counters["no_password"] += 1

                # 进度反馈
                if progress_every and counters["scanned"] % progress_every == 0:
                    print(
                        f"  …已扫描 {counters['scanned']} 个 ini，"
                        f"成功 {counters['success']}，"
                        f"失败 {counters['failed']}，"
                        f"无密码 {counters['no_password']}"
                    )

    return counters


# ============================================================
# 主入口
# ============================================================

def _maybe_inject_pause_for_frozen() -> None:
    """打包成 exe 双击运行时，自动启用 --pause（除非用户已显式指定）。"""
    if not getattr(sys, "frozen", False):
        return
    if "--pause" in sys.argv or "--no-pause" in sys.argv:
        return
    sys.argv.append("--pause")


def main() -> None:
    _maybe_inject_pause_for_frozen()

    # 1. 解析命令行
    args, _unknown = build_arg_parser().parse_known_args()

    # 2. 获取配置密码
    config_passphrase = _prompt_passphrase(args.passphrase)
    if config_passphrase is None:
        return
    print("密码输入完成，开始处理会话文件...\n")

    # 3. 解析 Sessions 目录并校验
    sessions_dir = resolve_sessions_dir(args.sessions_dir)
    print(f"使用Sessions目录: {sessions_dir}")
    if not os.path.isdir(sessions_dir):
        print(f"错误: 目录 '{sessions_dir}' 不存在，请检查路径是否正确。")
        if args.pause:
            _wait_for_enter("\n按 Enter 退出...")
        return

    # 4. 解析输出路径并执行批量处理
    output_csv = resolve_output_csv_path(args.output, sessions_dir)
    counters = process_sessions_dir(
        sessions_dir=sessions_dir,
        output_csv=output_csv,
        config_passphrase=config_passphrase,
        progress_every=args.progress_every,
    )

    # 5. 总结输出
    print(
        f"\n处理完成！扫描 {counters['scanned']} 个 ini，共记录 {counters['record']} 条："
        f"成功 {counters['success']}，"
        f"失败 {counters['failed']}，"
        f"仅用户名 {counters['no_password']}。"
    )
    print(f"结果已保存到：{output_csv}")
    print("警告：输出文件可能含敏感信息，请妥善保管或及时删除。")

    if args.pause:
        _wait_for_enter("\n处理完成，按 Enter 退出...")


if __name__ == "__main__":
    main()
