import socket as sk
import threading
from time import gmtime, strftime
from protocols import parse_request, create_message
from restaurantInfo import RestaurantInfo

HEADER = 32
FORMAT = 'utf-8'

LOGIN = 800
REGISTER = 802
DISCONNECT = 803
ORDER = 804
CHECK_DISCOUNT = 805
GET_MENU = 806
GET_RECEIPT = 807
USE_DISCOUNT = 808
CASH_OUT = 809

PORT = 5050
SERVER_IP = sk.gethostbyname(sk.gethostname())
ADDR = (SERVER_IP, PORT)

users = {
    "user1": {"password": "password1", "orders": []},
    "user2": {"password": "password2", "orders": []}
}

clients = {}

server = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
server.bind(ADDR)

restaurantInfo = RestaurantInfo()

def generate_receipt(orders, discount=0):
    items = {}
    
    for entry in orders:
        if entry:
            name, price = entry.split(', ')
            price = float(price)
            if name in items:
                items[name]['quantity'] += 1
                items[name]['total_price'] += price
            else:
                items[name] = {'quantity': 1, 'total_price': price}
    
    receipt_lines = []
    total = 0
    
    receipt_lines.append("Receipt")
    receipt_lines.append("=" * 40)
    
    for name, info in items.items():
        line = f"{info['quantity']:>2} x {name:<20} ${info['total_price']:>6.2f}"
        receipt_lines.append(line)
        total += info['total_price']
    
    if discount > 0:
        discount_amount = total * (discount / 100)
        total -= discount_amount
        receipt_lines.append(f"{'Discount':<22} -${discount_amount:>6.2f}")
    
    receipt_lines.append("=" * 40)
    receipt_lines.append(f"{'Total':<22} ${total:>6.2f}")
    
    return "\n".join(receipt_lines)

def handle_client(client_sk: sk.socket, addr):
    if client_sk:
        print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] New connection from {addr}")
        username = None
        connected = True
        
        while connected:
            try:
                msg_len = client_sk.recv(HEADER).decode(FORMAT).strip()
                if msg_len:
                    msg_len = int(msg_len)
                    command_status, command, data = parse_request(client_sk.recv(msg_len).decode(FORMAT))

                    if command_status == DISCONNECT:
                        send_message(client_sk, 202)
                        connected = False
                        if username:
                            del clients[username]
                        print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] {username} disconnected")
                        continue

                    if username is None:
                        if command_status == LOGIN:
                            username = data.get("username")
                            password = data.get("password")
                            
                            if username in users and users[username]["password"] == password and username not in clients:
                                clients[username] = client_sk
                                print(f'[{strftime("%Y-%m-%d %H:%M:%S", gmtime())}] {addr} successfully logged in as {username}')
                                print(f"[Action] Sent status 200 OK to {username} ({addr})")
                                send_message(client_sk, 200)
                            else:
                                print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] Login attempt failed for {addr}")
                                print(f"[Action] Sent status 400 Login failure to {addr}")
                                send_message(client_sk, 400)
                                username = None

                        elif command_status == REGISTER:
                            username = data.get("username")
                            password = data.get("password")

                            if username not in users:
                                users[username] = {"password": password, "orders": []}
                                print(f'[{strftime("%Y-%m-%d %H:%M:%S", gmtime())}] {addr} successfully registered as {username}')
                                print(f"[Action] Sent status 201 Created to {username} ({addr})")
                                send_message(client_sk, 201)
                                username = None

                            elif username in users:
                                print(f'[{strftime("%Y-%m-%d %H:%M:%S", gmtime())}] Registration attempt failed for {username} at {addr}: Username already in use')
                                print(f"[Action] Sent status 402 Username in use to {addr}")
                                send_message(client_sk, 402)
                                username = None

                            else:
                                print(f'[{strftime("%Y-%m-%d %H:%M:%S", gmtime())}] Registration attempt failed for {username} at {addr}')
                                print(f"[Action] Sent status 403 Registration failure to {addr}")
                                send_message(client_sk, 403)
                                username = None
                    else:
                        if command_status == ORDER:
                            order = data.get("order")
                            print(order)
                            if int(order) < len(restaurantInfo.getMenu()):
                                users[username]["orders"].append(f"{restaurantInfo.getMenu()[int(order)]}")
                                print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] {username} placed an order: {order}")
                                print(f"[Action] Sent status 200 OK to {username} ({addr}) with order confirmation")
                                send_message(client_sk, 200, f"Order received: {order}")
                            else:
                                print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] {username} attempted to order an invalid menu item: {order}")
                                print(f"[Action] Sent status 404 Menu item not found to {username} ({addr})")
                                send_message(client_sk, 404)

                        elif command_status == CHECK_DISCOUNT:
                            discounts = restaurantInfo.getDiscount()
                            ad = [discounts[i] for i in range(len(discounts)) if i % 2 == 1]
                            print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] {username} requested available discounts")
                            print(f"[Action] Sent status 200 OK to {username} ({addr}) with discounts")
                            send_message(client_sk, 200, f"Available discounts: {', '.join(ad)}")

                        elif command_status == GET_MENU:
                            menu = restaurantInfo.getMenu()
                            print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] {username} requested the menu")
                            print(f"[Action] Sent status 200 OK to {username} ({addr}) with menu")
                            send_message(client_sk, 200, f"Menu: {', '.join(menu)}")
                        
                        elif command_status == GET_RECEIPT:
                            orders = users[username]["orders"]
                            receipt = generate_receipt(orders)
                            
                            print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] {username} requested a receipt")
                            print(f"[Action] Sent status 200 OK to {username} ({addr}) with receipt")
                            send_message(client_sk, 200, f"Order queue: {receipt}")

                        elif command_status == USE_DISCOUNT:
                            discount_code = data.get("discount")
                            discount_value = restaurantInfo.getDiscountValue(discount_code)
                            
                            if discount_value is not None:
                                orders = users[username]["orders"]
                                receipt = generate_receipt(orders, discount_value)
                                print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] {username} applied discount code {discount_code}")
                                print(f"[Action] Sent status 200 OK to {username} ({addr}) with updated receipt")
                                send_message(client_sk, 200, f"Order queue with discount: {receipt}")
                            else:
                                print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] {username} attempted to use an invalid discount code: {discount_code}")
                                print(f"[Action] Sent status 406 Invalid discount code to {username} ({addr})")
                                send_message(client_sk, 406, "Invalid discount code.")
                        elif command_status == CASH_OUT:
                            users[username]["orders"] = []
                            print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] {username} cashed out")
                            print(f"[Action] Sent status 200 OK to {username} ({addr}) after cash out")
                            send_message(client_sk, 200, "Cash out: ")

                if not msg_len:
                    connected = False
                    if username:
                        del clients[username]
                    print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] Connection with {addr} closed")
                    continue

            except (ConnectionResetError, sk.error) as e:
                print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] Connection error: {e}")
                connected = False

            except Exception as e:
                print(f"[{strftime('%Y-%m-%d %H:%M:%S', gmtime())}] Error: {e}")
                connected = False
            
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
        print(f"[ACTIVE CONNECTIONS] Number of active connections: {threading.active_count() - 1}")

start_server()
