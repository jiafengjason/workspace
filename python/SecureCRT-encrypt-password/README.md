# SecureCRT 会话密码批量提取工具

一个用于离线还原 SecureCRT 会话 (`.ini`) 中保存密码的命令行工具。支持 SecureCRT 的两代密码格式（V1 双层 Blowfish、V2 AES 含 BCrypt-PBKDF2 派生），可批量遍历整个 `Sessions` 目录并把结果汇总为 CSV。

> ⚠️ **本工具仅用于您**自身**拥有合法访问权限的设备/账号**。误用或越权使用导致的任何后果由使用者自行承担。

---

## 目录结构

```
SecureCRT-encrypt-password/
├── securecrt_cipher.py              # SecureCRT V1 / V2 加解密算法实现（核心算法层）
├── securecrt_encrypt_password.py    # CLI 主入口：扫描 ini → 解密 → 写 CSV
├── requirements.txt                 # 运行时依赖（pycryptodome）
├── requirements_win7.txt            # Win7-11 打包专用依赖（锁定版本）
├── build_win7.bat                   # 一键打包脚本（生成 Win7-11 兼容 exe）
├── .gitignore                       # 忽略 CSV / Sessions / __pycache__ 等敏感物
├── LICENSE                          # MIT License
└── README.md                        # 本文档
```

运行时还会按需读写：

- `Sessions/`：SecureCRT 的会话目录（脚本同级，或由 `--sessions-dir` 指定，或回退到 `%APPDATA%\VanDyke\Config\Sessions`）。
- `securecrt_passwords.csv`：默认输出，位于 `Sessions/` 同级目录下。

---

## 核心特性

- **双版本兼容**：自动识别 `Password V2` (AES) 与 `Password` (V1 Blowfish)；同一会话同时存在时优先 V2，V2 失败可自动回退到 V1。
- **健壮的字段提取**：兼容 SecureCRT INI 文件末尾无换行、字符串字段含 hex 长度前缀等格式细节。
- **单文件异常隔离**：单个 ini 解析或解密失败不会中断整批处理，错误原因写入 CSV 的"备注"列。
- **状态与统计**：CSV 含 `状态`/`备注` 两列（`success`/`failed`/`no_password`），运行结束输出 `成功 / 失败 / 仅用户名` 计数。
- **Excel 友好的 CSV**：`utf-8-sig` BOM + `QUOTE_ALL`，密码含逗号/换行/引号也不会破坏列。
- **密码明文输入**：配置密码在终端明文显示输入，便于确认。
- **进度反馈**：每处理 N 条打印一行计数，N 由 `--progress-every` 控制。
- **打包友好**：被 PyInstaller 打包成 exe 双击运行时，自动启用 `--pause` 防止窗口闪退。

---

## 安装

```powershell
# 建议在虚拟环境中安装
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

仅需 `pycryptodome` 一个第三方依赖。

---

## 打包为 exe（Win7-11 兼容）

本工具提供一键打包脚本 `build_win7.bat`，可将程序打包为单个 exe 文件，兼容 Windows 7 SP1 / 8 / 10 / 11。

### 环境要求

| 项目 | 要求 |
|---|---|
| 操作系统 | Windows 7 SP1 及以上 |
| Python | **3.8.x**（推荐 3.8.10），64 位 |
| Windows 7 补丁 | 需安装 [KB2533623](https://support.microsoft.com/zh-cn/topic/2016%E5%B9%B46-%E6%9C%88%E5%AE%89%E5%85%A8%E6%9B%B4%E6%96%B0%E4%B8%AD-bf39f9f1-3f55-02cf-3d71-cbbbd1d85a3f) 和 [KB2999226](https://support.microsoft.com/zh-cn/topic/ucrt-dll-%E5%9C%A8%E8%AE%A1%E7%AE%97%E6%9C%BA%E4%B8%8A%E4%B8%8D%E5%8F%AF%E7%94%A8%E6%97%B6%E5%9C%A8-windows-server-2008-sp2-%E6%88%96-windows-vista-sp2-%E4%B8%8A%E5%AE%89%E8%A3%85-c-runtime-update-b695e5f4-a66b-28b6-f0d6-2f0b7f54d2cb)（Win10/11 无需） |

> 为什么选 Python 3.8？它是官方最后支持 Windows 7 的 Python 版本。更高版本可在 Win10/11 上使用，但打包后的 exe 无法在 Win7 上运行。

### 一键打包

```cmd
cd SecureCRT-encrypt-password
build_win7.bat
```

脚本会自动完成以下步骤：
1. 检测 Python 版本（3.8 ~ 3.10）
2. 升级 pip/setuptools/wheel 至兼容版本
3. 安装 `requirements_win7.txt` 中锁定的依赖（含 PyInstaller 4.10）
4. 验证 `pycryptodome` 内部 API `_bcrypt_hash` 可用
5. 清理旧构建产物
6. 执行 PyInstaller 打包为单文件 exe

打包成功后，输出文件位于：

```
dist\SecureCRT_Encrypt_Password.exe
```

### 手动打包

若需自行控制打包参数，可手动执行：

```cmd
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip==24.0 setuptools==69.5.1 wheel==0.43.0
pip install -r requirements_win7.txt

python -m PyInstaller --clean -F --console securecrt_encrypt_password.py ^
    --name=SecureCRT_Encrypt_Password ^
    --hidden-import=securecrt_cipher ^
    --hidden-import=Crypto.Cipher.AES ^
    --hidden-import=Crypto.Cipher.Blowfish ^
    --hidden-import=Crypto.Protocol.KDF._bcrypt_hash
```

### 分发与使用

1. 将 `SecureCRT_Encrypt_Password.exe` 拷贝到目标机器
2. 将 `Sessions` 目录放在 exe 同级目录下（或运行时通过 `--sessions-dir` 指定路径）
3. 双击 exe 运行，或在 CMD 中执行 `SecureCRT_Encrypt_Password.exe --help` 查看参数

> **注意**：exe 双击运行时会自动启用 `--pause`，程序结束后等待按回车才退出，防止窗口闪退。

---

## 使用方法

### 1. 准备 Sessions 目录

将 SecureCRT 的 `Sessions` 目录拷贝到本工具同级（或运行时通过参数指定路径）。SecureCRT 的默认位置：

```
%APPDATA%\VanDyke\Config\Sessions
```

### 2. 运行

最简形式（交互输入配置密码）：

```powershell
python securecrt_encrypt_password.py
```

常用参数：

```powershell
# 指定 Sessions 目录
python securecrt_encrypt_password.py --sessions-dir "C:\Users\me\AppData\Roaming\VanDyke\Config\Sessions"

# 指定输出 CSV 路径
python securecrt_encrypt_password.py -o passwords.csv

# 关闭进度输出
python securecrt_encrypt_password.py --progress-every 0

# 自动化场景：从命令行直接传配置密码（不推荐，会进入 shell 历史）
python securecrt_encrypt_password.py -p "<your-config-passphrase>"
```

完整参数：

| 参数 | 说明 |
|---|---|
| `--sessions-dir <path>` | SecureCRT Sessions 目录路径。默认顺序：脚本同级 `Sessions/` → `%APPDATA%\VanDyke\Config\Sessions` |
| `-o, --output <path>` | 输出 CSV 路径。默认：Sessions 同级目录下的 `securecrt_passwords.csv` |
| `-p, --passphrase <pwd>` | CRT 配置密码。**不推荐在命令行明文传入**，仅供自动化使用 |
| `--pause` | 结束后等待回车再退出（双击 exe 已自动启用） |
| `--progress-every <N>` | 每处理 N 个文件打印一条进度（默认 50；设为 0 关闭） |

### 3. 关于"配置密码"

SecureCRT V2 (`03:` 前缀) 密码使用用户在"全局选项 → 常规 → 配置密码"中设置的 **Configuration Passphrase** 作为派生密钥的 passphrase。

- 若你启用了配置密码，必须在交互提示处输入它，否则 V2 会话会全部解密失败。
- 若未启用（仅有 `02:` 前缀或 V1），直接按回车跳过即可。

---

## 输出 CSV 字段

| 列 | 含义 |
|---|---|
| 目录层级 | 会话相对 `Sessions/` 的子目录路径，分隔符替换为 `-`；位于根目录时为 `root` |
| 文件名 | `.ini` 文件名 |
| 用户名 | 会话中 `S:"Username"` 字段值 |
| 明文密码 | 解密成功时的明文；失败/无密码时为空 |
| 密码版本 | `V1` / `V2` / 空（无密码） |
| 状态 | `success` / `failed` / `no_password` |
| 备注 | 解密失败原因；V2 回退到 V1 时也会标注 |

---

## 模块说明

### `securecrt_cipher.py`

底层加解密原语，**不应被修改**（与 SecureCRT 的格式严格对应）：

- `SecureCRTCrypto`：V1 Blowfish-CBC 双层加密。
- `SecureCRTCryptoV2`：V2 AES-CBC，区分 `02` 前缀（SHA256 派生）与 `03` 前缀（随机 salt + bcrypt-pbkdf2 派生）。
- 也可作为独立 CLI 单条加/解密一段密文，参见文件内 `__main__` 部分。

### `securecrt_encrypt_password.py`

业务编排层，分若干清晰职责：

| 区段 | 主要函数 |
|---|---|
| INI 读取与解析 | `_read_ini_text`、`extract_password_info` |
| 解密策略 | `_decrypt_with_v1` / `_decrypt_with_v2` / `decrypt_password`（V2→V1 回退在此） |
| 路径与 CLI | `resolve_sessions_dir`、`resolve_output_csv_path`、`build_arg_parser`、`_prompt_passphrase` |
| 单文件 / 批量 | `_format_dir_level`、`_process_single_ini`、`process_sessions_dir` |
| 主入口 | `_maybe_inject_pause_for_frozen`、`main` |

所有正则在模块加载时一次性编译，频繁字段提取无重复开销。

---

## 安全提示

- 输出 CSV 中**包含明文密码**。建议处理完毕后立即妥善归档（加密 zip、删除原文件等），勿提交到任何仓库。
- 仓库 `.gitignore` 已默认忽略 `*.csv` / `*.ini` / `Sessions/`。
- 配置密码请使用交互输入（默认行为），避免出现在 shell 历史或 CI 日志中。
- 本工具使用了 `pycryptodome` 中的内部 API `Crypto.Protocol.KDF._bcrypt_hash`（V2 `03:` 前缀派生需要）。升级 `pycryptodome` 时若出现 `AttributeError`，将版本回退到 `requirements.txt` 锁定的范围即可。

---

## 常见问题

**Q：所有 V2 会话均报 `无效密文: 明文长度不正确`？**
A：99% 是配置密码输入错误。请确认你输入的是 SecureCRT "全局选项 → 常规 → 配置密码"中的密码；若该选项未启用，则直接回车。

**Q：双击 exe 后窗口一闪而过？**
A：本工具在 frozen 模式下会自动启用 `--pause`，若仍然闪退，多半是依赖未一同打包，请用 `console=True` 模式构建 PyInstaller 并查看错误。

**Q：能不能用在 Linux/Mac？**
A：核心算法跨平台，CLI 主体也跨平台，但 `Sessions` 目录的默认查找路径基于 `%APPDATA%`。在 *nix 上请显式 `--sessions-dir`。

---

## 致谢

底层算法实现参考自社区已有的 SecureCRT 解密工作（`securecrt_cipher.py`），原作者请见文件头部注释或开源参考。

---

## License

本项目以 [MIT License](./LICENSE) 发布。`securecrt_cipher.py` 中借鉴自第三方的算法实现部分，请额外尊重其原始许可证。
