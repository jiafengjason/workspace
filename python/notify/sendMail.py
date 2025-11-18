import smtplib
import ssl
from email.message import EmailMessage

def send_email(sender, password, receiver, subject, body):
    smtp_server = "smtp.qiye.aliyun.com"
    port = 465

    # 设置邮件内容
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    # 创建SSL安全上下文并发送邮件
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender, password)
            server.send_message(msg, from_addr=sender, to_addrs=receiver)
        print("邮件发送成功！")
    except Exception as error:
        print(f"发送失败: {error}")

if __name__ == "__main__":
    sender_email = "jiafeng@enlink.cn"  # 替换为你的Gmail地址
    app_password = "ZhMpKAl3fXvzJz2C"     # 替换为你的Gmail应用专用密码
    receiver_email = "jiafeng@enlink.cn"
    email_subject = "这是一封测试邮件"
    email_body = "你好，这封邮件是通过Python发送的！"

    send_email(sender_email, app_password, receiver_email, email_subject, email_body)