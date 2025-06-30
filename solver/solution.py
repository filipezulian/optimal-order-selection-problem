class Solution:
    def __init__(self, order_ids, aisle_ids, item_totals):
        self.order_ids = order_ids
        self.aisle_ids = aisle_ids
        self.item_totals = item_totals
    
    def evaluate(self):
        total_items = sum(self.item_totals.values())
        num_aisles = len(self.aisle_ids)
        
        if num_aisles == 0:
            return 0
        
        return total_items / num_aisles
    
    def is_feasible(self, instance):
        total_items = sum(self.item_totals.values())
        
        #valida limites
        if total_items < instance.lb or total_items > instance.ub:
            return False
        
        #verifica se a quantidade pode ser atendida com os corredores usados
        for item_id, needed_quantity in self.item_totals.items():
            available_quantity = 0
            for aisle_id in self.aisle_ids:
                aisle = instance.aisles[aisle_id]
                if item_id in aisle:
                    available_quantity += aisle[item_id]
            
            if available_quantity < needed_quantity:
                return False
        
        return True