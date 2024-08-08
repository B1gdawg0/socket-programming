import socket as sk
import threading
import time
from protocols import create_request, parse_message

HEADER = 32
FORMAT = 'utf-8'
DISCONNECT_MSG = "/DISCONNECT"
OK = 200
USER_LOGOUT = 202
REGISTER_SUCCESS = 201
LOGIN_FAILURE = 400
MENU_NOT_FOUND = 404
USERNAME_ALREADY_USE = 402
INVALID_DISCOUNT = 406
PORT = 5050
SERVER_IP = sk.gethostbyname(sk.gethostname())
ADDR = (SERVER_IP, PORT)

class KFCClient:
    def __init__(self, server_ip, port):
        self.addr = (server_ip, port)
        self.client_sk = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.client_sk.connect(self.addr)

    def send(self, command: str, data={"":""}):
        msg = create_request(command, data)
        msg_enc = msg.encode(FORMAT)
        msg_enc_len = len(msg_enc)
        send_len = str(msg_enc_len).encode(FORMAT)
        send_len += b' ' * (HEADER - len(send_len))
        self.client_sk.send(send_len)
        self.client_sk.send(msg_enc)

    def receive(self):
        while True:
            msg_len = self.client_sk.recv(HEADER).decode(FORMAT).strip()
            if msg_len:
                msg_len = int(msg_len)
                code, status_message, data = parse_message(self.client_sk.recv(msg_len).decode(FORMAT))
                if code == USER_LOGOUT:
                    print(f"[{code} {status_message}] Logout request successful!")
                    break

                elif code == OK: 
                    if "Order received" in data:
                        print(f"[{code} {status_message}] Your order has been received!")
                    elif "Available discounts" in data:
                        print(f"[{code} {status_message}] Available discounts request successful!")
                        discounts = data.split("Available discounts: ")[1].split(", ")
                        for discount in discounts:
                            print(f'-> {discount}')
                    elif "Menu" in data:
                        print(f"[{code} {status_message}] Menu request successful!")
                        content = data.split("Menu: ")[1].strip()
                        items = content.split(", ")

                        menu = []
                        prices = []

                        for i in range(0, len(items)):
                            if i % 2 == 0:
                                menu.append(items[i].strip())
                            else:
                                prices.append(items[i].strip())

                        for i in range(len(menu)):
                            print(f"[{i}] {menu[i]} is ${prices[i]}")


                    elif "Order queue with discount" in data:
                        print(f"[{code} {status_message}] Discount request successful!")
                        print(f'\n{data.split("Order queue with discount: ")[1]}')
                    
                    elif "Order queue" in data:
                        print(f"[{code} {status_message}] Receipt request successful!")
                        print(f'\n{data.split("Order queue: ")[1]}')

                    elif "Cash out" in data:
                        print(f"[{code} {status_message}] Cash out request successful!")

                    else:
                        print(f"[{code} {status_message}] Something went wrong!")
                elif code == MENU_NOT_FOUND:
                    print(f"[{code} {status_message}] Menu item does not exist. Please try again with a valid number.")
                elif code == INVALID_DISCOUNT:
                    print(f"[{code} {status_message}] Invalid discount. Please try another discount code.")
                else:
                    print(f"[{code} {status_message}] Something went wrong!")
            else:
                break

    def login(self):
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        self.send("/LOGIN", {"username": username, "password": password})

        response_len = self.client_sk.recv(HEADER).decode(FORMAT).strip()
        if response_len:
            response_len = int(response_len)
            code, status_message, data = parse_message(self.client_sk.recv(response_len).decode(FORMAT))

        if code == OK:
            print(f"[{code} {status_message}] Login successful!")
            recv_thread = threading.Thread(target=self.receive)
            recv_thread.start()
            self.user_menu()
        else:
            print(f"[{code} {status_message}] Login failed!")

    def register(self):
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        self.send("/REGISTER", {"username": username, "password": password})

        response_len = self.client_sk.recv(HEADER).decode(FORMAT).strip()
        if response_len:
            response_len = int(response_len)
            code, status_message, data = parse_message(self.client_sk.recv(response_len).decode(FORMAT))

        if code == REGISTER_SUCCESS:
            print(f"[{code} {status_message}] Registration successful!")
        elif code == USERNAME_ALREADY_USE:
            print(f"[{code} {status_message}] This username is already in use. Please try another username.")
        else:
            print(f"[{code} {status_message}] Registration failed!")

    def user_menu(self):
        while True:
            time.sleep(0.3)
            print("\n1. Order food")
            print("2. Check available discounts")
            print("3. View menu")
            print("4. Cash out")
            print("Q. Logout")
            user_input = input("Choose an option: ").strip()

            if user_input == '1':
                self.send("/GET_MENU")
                time.sleep(0.3) 
                order = ""
                while not order:
                    order = input("Enter your menu number: ").strip()
                    if order.isdigit() and int(order) >= 0:
                        self.send("/ORDER", {"order": order})
                    else:
                        print("Invalid menu number. Please try again.")
                        order = ""
            elif user_input == '2':
                self.send("/CHECK_DISCOUNT")
            elif user_input == '3':
                self.send("/GET_MENU")
            elif user_input == '4':
                self.send("/GET_RECEIPT")
                time.sleep(0.3)
                while True:
                    check = input("Would you like to use a discount? Y/C (Y = Yes, C = Cash out): ").strip().upper()
                    if check == "Y":
                        discount = input("Enter discount code: ").strip()
                        if discount:
                            self.send("/USE_DISCOUNT", {"discount": discount})
                            time.sleep(0.3)
                        else:
                            print("Please enter a discount code before sending.")
                    elif check == "C":
                        self.send("/CASH_OUT")
                        break
                    else:
                        print("Invalid option. Please try again.")

            elif user_input.upper() == 'Q':
                self.send("/LOGOUT")
                break
            else:
                print("Invalid option. Please try again.")

    def start(self):
        print("Welcome to KFC online ordering. Login to order now!")
        while True:
            time.sleep(0.3)
            auth = input("Do you already have an account? Y/N/Q (Y = Yes, N = No, Q = Quit): ").strip().upper()
            if auth == "Y":
                self.login()
            elif auth == "N":
                interest_check = input("Enter R to register or Q to quit: ").strip().upper()
                if interest_check == "R":
                    self.register()
                elif interest_check == "Q":
                    break
                else:
                    print("Please enter R or Q only.")
            elif auth == "Q":
                break
            else:
                print("Please enter Y, N, or Q only.")

        self.client_sk.close()

if __name__ == "__main__":
    client = KFCClient(SERVER_IP, PORT)
    client.start()
