import socket as sk
import threading
from protocols import create_request,parse_message

HEADER = 32
FORMAT = 'utf-8'
DISCONNECT_MSG = "/DISCONNECT"
LOGIN_SUCCESS = 200
REGISTER_SUCCESS = 201
LOGIN_FAILURE = 400
USERNAME_ALREADY_USE = 402
PORT = 5050
SERVER_IP = sk.gethostbyname(sk.gethostname())
ADDR = (SERVER_IP, PORT)

client_sk = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
client_sk.connect(ADDR)

def send(command:str, data={}):
    msg = create_request(command,data)
    msg_enc = msg.encode(FORMAT)
    msg_enc_len = len(msg_enc)
    send_len = str(msg_enc_len).encode(FORMAT)
    send_len += b' ' * (HEADER - len(send_len))
    client_sk.send(send_len)
    client_sk.send(msg_enc)
    

def receive():
    while True:
        msg_len = client_sk.recv(HEADER).decode(FORMAT).strip()
        if msg_len:
            msg_len = int(msg_len)
            msg = client_sk.recv(msg_len).decode(FORMAT)
            print(f"\n{msg}")
            print("Enter message (or type '%q' to exit): ", end="")


def login():
    username = input("Enter username: ")
    password = input("Enter password: ")
    send("/LOGIN",{"username":username, "password":password})

    response_len = client_sk.recv(HEADER).decode(FORMAT).strip()

    if response_len:
        response_len = int(response_len)
        code, status_message, data = parse_message(client_sk.recv(response_len).decode(FORMAT))

    if code == LOGIN_SUCCESS:
        print(f"[{code} {status_message}] Login successful!")
        
        recv_thread = threading.Thread(target=receive)
        recv_thread.start()

        # implement here (LOGIN part)
        
    else:
        print(f"[{code} {status_message}] Login failed!")

def register():
    username = input("Enter username: ")
    password = input("Enter password: ")
    send("/REGISTER",{"username":username, "password":password})

    response_len = client_sk.recv(HEADER).decode(FORMAT).strip()

    if response_len:
        response_len = int(response_len)
        code, status_message, data = parse_message(client_sk.recv(response_len).decode(FORMAT))

    if code == REGISTER_SUCCESS:
        print(f"[{code} {status_message}] Register successful!")
        
        recv_thread = threading.Thread(target=receive)
        recv_thread.start()
        
        # implement here (REGISTER part)

    elif code == USERNAME_ALREADY_USE:
        print(f"[{code} {status_message}] This username is already use by someone. Please try other username again")

    else :
        print(f"[{code} {status_message}] Register fail!")

print("Welcome to online KFC ordering. Login to order now!")
while True:
    auth = input("Do you already have account? Y/N/Q(Y for yes and N for no and Q for CLOSE PROGRAM)")
    if auth.upper() == "Y":
        login()

    elif auth.upper() == "N":
        interest_check = input("Enter R/Q (R for Register and Q for CLOSE PROGRAM)")
        if interest_check.upper() == "R":
            register()
        elif interest_check.upper() == "Q":
            break
        else:
            print("Please Enter Y or N or Q only")

    elif auth.upper() == "Q":
        break
        
    else:
        print("Please Enter Y or N or Q only")

client_sk.close()
