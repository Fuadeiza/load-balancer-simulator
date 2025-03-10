import socket
import threading

LIST_OF_ADDR = [
    ("127.0.0.1", 9001),
    ("127.0.0.1", 9002),
    ("127.0.0.1", 9003)
]

def handle_backend(conn, addr, port):
    print(f"[BACKEND {port}] New connection from {addr}")

    while True:
        try:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            print(f"[BACKEND {port}] Received: {msg}")
            response = f"Processed by {port}" 
            conn.send(response.encode())
        except ConnectionResetError:
            break

    print(f"[BACKEND {port}] Connection closed with {addr}")
    conn.close()

def start_backend_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[BACKEND {port}] Server listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_backend, args=(conn, addr, port))
        thread.start()

for host, port in LIST_OF_ADDR:
    thread = threading.Thread(target=start_backend_server, args=(host, port), daemon=False)
    thread.start()
