import socket
import threading
import sys
import signal

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9843
ADDR = (HOST, PORT)
DISCONNECT_MSG = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()

backend_servers = [
    ("127.0.0.1", 9001),
    ("127.0.0.1", 9002),
    ("127.0.0.1", 9003)
]

current_server = 0

def is_server_alive(addr):
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(1)
        test_socket.connect(addr)
        test_socket.close()
        return True
    except:
        return False

def handle_client(conn, addr):
    global current_server
    print(f"[NEW CONNECTION] {addr} connected")

    try:
        while True:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            
            print(f"Received this message: {msg} from {addr}")

            for _ in range(len(backend_servers)):
                backend_addr = backend_servers[current_server]
                current_server = (current_server + 1) % len(backend_servers)

                if is_server_alive(backend_addr):
                    break
            else:
                print("[ERROR] No backend servers available!")
                conn.send("503 Service Unavailable".encode())
                continue

            print(f"Forwarding CLIENT {addr} message to server {backend_addr}")
            backend_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            backend_conn.connect(backend_addr)
            backend_conn.send(msg.encode())

            response = backend_conn.recv(1024).decode()
            backend_conn.close()

            print(f"Sending {response} from {backend_addr} to client {addr}")
            conn.send(response.encode())

            if msg == DISCONNECT_MSG:
                break  

    except ConnectionResetError:
        print(f"[ERROR] Connection lost with {addr}")

    finally:
        print(f"[DISCONNECTING] {addr} disconnected")
        conn.close()

def start():
    print(f"[STARTING] Load Balancer running on {HOST}:{PORT}...")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

def signal_handler(sig, frame):
    print("\n[SHUTTING DOWN] Closing Load Balancer...")
    server.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

start()
_