class RestaurantInfo:
    def __init__(self):
        self.menu_file = "data/menu.txt"
        self.discount_file = "data/discount.txt"
    
    def getMenu(self):
        return self._read_file(self.menu_file)
    
    def getDiscount(self):
        return self._read_file(self.discount_file)
    
    def getDiscountValue(self, discount_code):
        discounts = self.getDiscount()
        for i in range(0, len(discounts), 2):
            code, value = discounts[i].split(":")
            if code == discount_code:
                return int(value)
        return None
    
    def _read_file(self, file_path):
        with open(file_path, 'r') as file:
            return file.read().strip().split('\n')
