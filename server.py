import socket as sk
import threading
from time import gmtime, strftime
from protocols import parse_request, create_message

HEADER = 32
FORMAT = 'utf-8'

LOGIN = 800
REGISTER = 802
DISCONNECT = 803

PORT = 5050
SERVER_IP = sk.gethostbyname(sk.gethostname())
ADDR = (SERVER_IP, PORT)

users = {
    "user1": "password1",
    "user2": "password2"
}

clients = {}

server = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
server.bind(ADDR)

def handle_client(client_sk: sk.socket, addr):
    if client_sk:
        print(f"[NEW CONNECTION] {addr} connected")
        username = None
        connected = True
        
        while connected:
            try:
                msg_len = client_sk.recv(HEADER).decode(FORMAT).strip()
                if msg_len:
                    msg_len = int(msg_len)
                    command_status, command, data = parse_request(client_sk.recv(msg_len).decode(FORMAT))

                    if command_status == DISCONNECT:
                        connected = False
                        if username:
                            del clients[username]
                        continue

                    if username is None:
                        if command_status == LOGIN:
                            username = data.get("username")
                            password = data.get("password")
                            
                            if username in users and users[username] == password and username not in clients:
                                clients[username] = client_sk
                                print(f'[{strftime("%Y-%m-%d %H:%M:%S", gmtime())}] {addr} logged in as {username}')
                                print(f"[Action] Sent status 200 OK to {username} {addr})")
                                send_message(client_sk, 200)
                            else:
                                print(f"[Action] Sent status 400 Login Login failure to {addr})")
                                send_message(client_sk, 400)
                        elif command_status == REGISTER:
                            username = data.get("username")
                            password = data.get("password")

                            if username not in users:
                                users[username] = password
                                print(f'[{strftime("%Y-%m-%d %H:%M:%S", gmtime())}] {addr} registered as {username}')
                                print(f"[Action] Sent status 201 Created to {username} {addr})\n")
                                send_message(client_sk, 201)

                            elif username in users:
                                print(f"[Action] Sent status 402 Username is already use to {addr})")
                                send_message(client_sk, 402)

                            else :
                                print(f"[Action] Sent status 403 Register failure to {addr})")
                                send_message(client_sk, 403)
                    else:
                        pass
                
                if not msg_len:
                    break

            except (ConnectionResetError, sk.error) as e:
                print(f"Connection error: {e}")
                connected = False

            except Exception as e:
                print(f"Error: {e}")
                connected = False
            
            username = None

    client_sk.close()

def send_message(client_sk: sk.socket, code, data=""):
    msg = create_message(code, data)
    msg_enc = msg.encode(FORMAT)
    msg_enc_len = len(msg_enc)
    send_len = str(msg_enc_len).encode(FORMAT)
    send_len += b' ' * (HEADER - len(send_len))
    client_sk.send(send_len)
    client_sk.send(msg_enc)

def start_server():
    print("[STARTING] Server is running...")
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] Number of user's connection with this server {threading.active_count() - 1}")

start_server()
