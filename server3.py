import socket
import threading

HOST = '127.0.0.1'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = {}  # username: conn

def handle_client(conn, addr):
    username = conn.recv(1024).decode()
    clients[username] = conn
    print(f"{username} connected from {addr}")

    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            target, msg = data.split(":", 1)
            if target in clients:
                clients[target].send(f"[{username}] {msg}".encode())
            else:
                conn.send(f"User '{target}' not found.".encode())
    except:
        pass
    finally:
        conn.close()
        del clients[username]
        print(f"{username} disconnected")

def start():
    print("Server running...")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start()
