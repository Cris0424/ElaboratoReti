import socket
import os
import mimetypes
from datetime import datetime

HOST, PORT = '127.0.0.1', 8080
ROOT_DIR = './www'

def log_request(method, path, status):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] {method} {path} -> {status}")

def handle_client(client_socket):
    request = client_socket.recv(1024).decode('utf-8')
    lines = request.split('\r\n')
    if not lines:
        client_socket.close()
        return

    request_line = lines[0]
    try:
        method, path, _ = request_line.split()
    except ValueError:
        client_socket.close()
        return

    if method != 'GET':
        client_socket.close()
        return

    if path == '/':
        path = '/index.html'

    file_path = os.path.join(ROOT_DIR, path.lstrip('/'))
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        response = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\n\r\n".encode('utf-8') + content
        log_request(method, path, 200)
    else:
        response_body = "<h1>404 Not Found</h1>".encode('utf-8')
        response = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n" + response_body
        log_request(method, path, 404)

    client_socket.sendall(response)
    client_socket.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server in ascolto su http://{HOST}:{PORT}")

        while True:
            client_socket, _ = server_socket.accept()
            handle_client(client_socket)

if __name__ == '__main__':
    start_server()
