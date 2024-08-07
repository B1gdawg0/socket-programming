class Restaurant:
    def __init__(self, username):
        self.username = username
        self.income = 0
        self.menu = {}
        self.order_queue = []

    def run(self):
        print(f"You're login as a {self.username} restaurant ")
        

    def add_to_menu(self, item, price):
        self.menu[item] = price

    def remove_from_menu(self, item):
        if item in self.menu:
            del self.menu[item]

    def update_menu_item(self, item, price):
        if item in self.menu:
            self.menu[item] = price

    def show_menu(self):
        return self.menu

    def receive_order(self, customer_id, order):
        self.order_queue.append(order)
        return len(self.order_queue)
    

    def process_order(self, order_number):
        if self.order_queue:
            order = self.order_queue.pop(order_number)
            return f"Order NO.{order_number} done!"
        return f"Don't has this number in queue"

    def __str__(self):
        return f"Restaurant: {self.name}, Money: {self.money}, Menu: {self.menu}, Orders: {len(self.order_queue)}"
