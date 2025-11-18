#openssl genrsa -out private_key.pem 2048
#openssl rsa -in private_key.pem -pubout -out public_key.pem
import hashlib
import platform
import uuid
import psutil # 需要安装：pip install psutil
import json
from datetime import datetime,timedelta
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

def generate_rsa_keys():
    """生成RSA公钥和私钥对"""
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # 保存私钥 (PKCS#8格式)
    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # 保存公钥
    public_key = private_key.public_key()
    with open("public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    
    print("RSA密钥对已生成：")
    print("- private_key.pem (私钥，用于生成许可证，请妥善保管)")
    print("- public_key.pem (公钥，用于验证许可证)")

def get_machine_fingerprint():
    """
    组合多个系统信息生成一个机器指纹。
    返回一个MD5哈希字符串。
    """
    fingerprint_data = ""

    # 1. 获取主板UUID（推荐，比较稳定）
    try:
        motherboard_uuid = platform.node() # 通常是主机名，作为备选
        # 更可靠的方法（Windows）：
        # import subprocess
        # result = subprocess.check_output('wmic csproduct get uuid', shell=True).decode().split('\n')[1].strip()
        # fingerprint_data += result
    except:
        motherboard_uuid = "unknown_motherboard"
    fingerprint_data += motherboard_uuid

    # 2. 获取硬盘序列号（通常是C盘）
    try:
        disk_serial = psutil.disk_partitions()[0].device # 取第一个分区
        # 注意：在非Windows系统上获取磁盘序列号更复杂，可能需要其他命令
    except:
        disk_serial = "unknown_disk"
    fingerprint_data += disk_serial

    # 3. 获取MAC地址
    try:
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
    except:
        mac_address = "unknown_mac"
    fingerprint_data += mac_address

    # 4. 将组合的信息进行MD5哈希，得到固定长度的指纹
    return hashlib.md5(fingerprint_data.encode('utf-8')).hexdigest()

def generate_license_file(customer_name, days_valid, machine_fingerprint, output_file="license.lic"):
    """
    生成一个许可证文件
    """
    # 1. 构造授权数据
    issue_date = datetime.now().strftime("%Y-%m-%d")
    expiry_date = (datetime.now() + timedelta(days=days_valid)).strftime("%Y-%m-%d")

    license_data = {
        "customer_name": customer_name,
        "product_key": "MY-PYTHON-APP",
        "machine_fingerprint": machine_fingerprint,
        "issue_date": issue_date,
        "expiry_date": expiry_date
    }

    # 2. 将数据转换为JSON字符串
    license_json = json.dumps(license_data, indent=2)

    # 3. 使用私钥进行签名
    try:
        with open("private_key.pem", "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
    except FileNotFoundError:
        print("错误：未找到 private_key.pem 文件")
        print("请先运行 generate_keys.py 生成密钥对")
        return None

    # 对数据进行签名
    signature = private_key.sign(
        license_json.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # 4. 将许可证数据和签名一起保存到文件
    license_package = {
        "data": license_data,
        "signature": signature.hex() # 将字节转换为十六进制字符串以便存储
    }

    with open(output_file, 'w') as f:
        json.dump(license_package, f, indent=2)

    print(f"许可证已生成: {output_file}")
    print(f"客户: {customer_name}")
    print(f"有效期: {issue_date} 至 {expiry_date}")
    print(f"机器指纹: {machine_fingerprint}")
    return output_file

def verify_license(license_file_path="license.lic"):
    """
    验证许可证是否有效
    返回 (is_valid, message)
    """
    try:
        # 1. 读取许可证文件
        with open(license_file_path, 'r') as f:
            license_package = json.load(f)

        license_data = license_package["data"]
        signature = bytes.fromhex(license_package["signature"])

        # 2. 使用公钥验证签名
        try:
            with open("public_key.pem", "rb") as f:
                public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
        except FileNotFoundError:
            return False, "未找到公钥文件"

        # 重新序列化数据用于验证
        license_json = json.dumps(license_data, indent=2)

        # 验证签名
        try:
            public_key.verify(
                signature,
                license_json.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except InvalidSignature:
            return False, "许可证签名无效，文件可能被篡改。"

        # 3. 验证机器指纹是否匹配
        current_fingerprint = get_machine_fingerprint()
        if license_data["machine_fingerprint"] != current_fingerprint:
            return False, "许可证与当前机器不匹配。"

        # 4. 验证有效期
        expiry_date = datetime.strptime(license_data["expiry_date"], "%Y-%m-%d")
        if datetime.now() > expiry_date:
            return False, "许可证已过期。"

        # 5. 所有检查都通过
        return True, f"许可证有效，用户：{license_data['customer_name']}，有效期至：{license_data['expiry_date']}"

    except FileNotFoundError:
        return False, "未找到许可证文件。"
    except Exception as e:
        return False, f"验证许可证时发生未知错误: {str(e)}"

if __name__ == "__main__":
    #generate_rsa_keys()

    fingerprint = get_machine_fingerprint()
    print(f"本机指纹: {fingerprint}")

    generate_license_file("test", 365, fingerprint)
    
    is_valid, message = verify_license()
    print(f"验证结果: {is_valid}")
    print(f"验证信息: {message}")
