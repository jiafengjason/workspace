import http.server
import socketserver
import ssl

# 创建 HTTP 服务器
PORT = 4443
httpd = socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler)

# 创建 SSL 上下文
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

# 使用 SSLContext.wrap_socket() 封装套接字
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

# 启动服务器
print(f"Serving on https://localhost:{PORT}")
httpd.serve_forever()