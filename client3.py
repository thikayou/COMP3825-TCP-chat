import socket
import threading

HOST = '127.0.0.1'
PORT = 5555

username = input("Enter your username: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(username.encode())

def receive_messages():
    while True:
        try:
            msg = client.recv(1024).decode()
            print("\n" + msg)
        except:
            break

def send_messages():
    while True:
        target = input("Send to (username): ")
        msg = input("Message: ")
        full_msg = f"{target}:{msg}"
        client.send(full_msg.encode())

recv_thread = threading.Thread(target=receive_messages)
recv_thread.start()

send_messages()
