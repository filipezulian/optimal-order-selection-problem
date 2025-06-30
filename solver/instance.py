from collections import defaultdict

class Instance:
    def __init__(self, n_orders, n_items, n_aisles, orders, aisles, lb, ub):
        self.n_orders = n_orders
        self.n_items = n_items
        self.n_aisles = n_aisles
        self.orders = orders
        self.aisles = aisles
        self.lb = lb
        self.ub = ub
    
    @staticmethod
    def from_file(path):
        with open(path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        n_orders, n_items, n_aisles = map(int, lines[0].split())
        idx = 1
        
        orders = []
        for order_idx in range(n_orders):
            parts = list(map(int, lines[idx].split()))
            k = parts[0]
            order = {parts[i]: parts[i + 1] for i in range(1, 2 * k + 1, 2)}
            orders.append(order)
            idx += 1
        
        aisles = []
        for aisle_idx in range(n_aisles):
            parts = list(map(int, lines[idx].split()))
            k = parts[0]
            aisle = {parts[i]: parts[i + 1] for i in range(1, 2 * k + 1, 2)}
            aisles.append(aisle)
            idx += 1
        
        lb, ub = map(int, lines[idx].split())
        
        return Instance(n_orders, n_items, n_aisles, orders, aisles, lb, ub)