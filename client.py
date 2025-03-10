import socket

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9843
ADDR = (HOST, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

while True:
    msg = input("Enter message: ")
    client.send(msg.encode())

    response = client.recv(1024).decode()
    print(f"Server response: {response}")

    if msg == "!DISCONNECT":
        break

client.close()
