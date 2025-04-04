import socket
import threading
import signal
import sys
import ssl

HOST = '141.225.193.199'
PORT = 55516
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind((HOST, PORT))
# server.listen()

# List to keep track of connected clients
clients = {}
usernames = {}
SERVER_CERT = 'server.crt'
SERVER_KEY = 'server.key'


# Function to handle client communication
def handle_client(client_socket, client_address):
    # Sending the list of active users
    client_socket.send("Welcome to the chat room!\nUsers currently online:\n".encode())
    send_active_users(client_socket)

    while True:
        try:
            # Receiving the message from the client
            message = client_socket.recv(1024).decode()
            if message:
                # If the user types .exit, disconnect them
                if message.strip() == '.exit':
                    remove_client(client_socket)
                    break
                
                # Check if it's a private message
                if message.startswith("/@"):
                    handle_private_message(message, client_socket)
                else:
                    # Broadcasting the message to all clients
                    broadcast(message, client_socket)
            else:
                break
        except:
            break

    remove_client(client_socket)

# Function to handle private messages
def handle_private_message(message, sender_socket):
    try:
        # Parse the /@ <username> <message>
        parts = message.split(" ", 2)
        if len(parts) < 3:
            sender_socket.send("Invalid private message format. Use: /@ <username> <message>\n".encode())
            return

        target_username = parts[1]
        private_message = parts[2]

        # Find the recipient socket
        recipient_socket = None
        for socket, username in usernames.items():
            if username == target_username:
                recipient_socket = socket
                break

        if recipient_socket:
            sender_username = usernames[sender_socket]
            recipient_socket.send(f"Private message from {sender_username}: {private_message}\n".encode())
            sender_socket.send(f"Private message to {target_username}: {private_message}\n".encode())
        else:
            sender_socket.send(f"User {target_username} not found.\n".encode())
    except Exception as e:
        print(f"Error handling private message: {e}")

# Function to broadcast message to all clients
def broadcast(message, sender_socket):
    for client_socket in clients:
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode())
            except:
                continue

# Send the list of active users to the new client
def send_active_users(client_socket):
    for username in usernames.values():
        client_socket.send(f"{username}\n".encode())

# Remove a client from the server
def remove_client(client_socket):
    username = usernames.pop(client_socket, None)
    if username:
        clients.pop(client_socket, None)
        broadcast(f"{username} has left the chat.\n", client_socket)
        client_socket.close()

def stop_server(signal_num, frame):
    print("Shutting down the server...")

    for client_socket in list(clients.keys()):
        remove_client(client_socket)
    print("All connections closed")
    sys.exit(0)

# Main server function
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))  # Host on all interfaces at port 5555
    server.listen(5)
    print("Server started... Waiting for clients to connect.")
    # server = ssl.wrap_socket(server, keyfile=SERVER_KEY, certfile=SERVER_CERT, server_side=True)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)
    
    signal.signal(signal.SIGINT, stop_server)

    
    while True:
        client_socket, client_address = server.accept()
        print(f"New connection from {client_address}")
        
        server=context.wrap_socket(client_socket, server_side=True)
        
        # Ask for the username
        client_socket.send("Enter your username: ".encode())
        username = client_socket.recv(1024).decode().strip()
        
        # Save the client and username
        clients[client_socket] = client_address
        usernames[client_socket] = username
        
        # Send welcome message and the list of active users
        
        client_socket.send(f"Hello {username}! You are now connected.\n".encode())
        
        # Start a new thread to handle this client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()


start_server()
