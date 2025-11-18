import speedtest

def test_internet_speed():
    """
    测试下载和上传速度
    """
    st = speedtest.Speedtest()
    download_speed = st.download() / 1024 / 1024  # 将下载速度转换为 Mbps
    upload_speed = st.upload() / 1024 / 1024  # 将上传速度转换为 Mbps

    print("下载速度: {:.2f} Mbps".format(download_speed))
    print("上传速度: {:.2f} Mbps".format(upload_speed))

if __name__ == "__main__":
    print("开始测试网速...")
    test_internet_speed()
