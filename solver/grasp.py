import random
import time
from solution import Solution

def grasp_solve(instance, iterations=10, randomizer=0.3, timeout=60):
    best_solution = None
    best_score = -1
    start_time = time.time()
    no_improvement_count = 0
    no_improvement_limit = max(10, iterations // 10)
    
    # em vez de calcular o tamanho medio dos pedidos e capacidade dos corredorest toda vez
    # calculo uma vez no comeco e reutilizo, pra ir mais rapido
    stats = get_instance_stats(instance)
    
    for iteration in range(iterations):
        elapsed_time = time.time() - start_time
        if timeout and elapsed_time > timeout:
            print(f"Timeout {iteration} iterações")
            break
        
        solution = construct_solution(instance, randomizer, stats)
        
        solution = local_search(solution, instance, stats)
        
        score = solution.evaluate()
        
        if score > best_score:
            best_solution = solution
            best_score = score
            no_improvement_count = 0
            print(f"Nova melhor solução: {best_score:.3f} (iter {iteration})")
        else:
            no_improvement_count += 1
        
        # limite de iteracoes sem melhorias
        if no_improvement_count >= no_improvement_limit:
            print(f"Passou de {no_improvement_count} iterações sem melhoria")
            break
    
    return best_solution

def get_instance_stats(instance):
    stats = {}
    
    # Order statistics
    order_sizes = [sum(order.values()) for order in instance.orders]
    stats['avg_order_size'] = sum(order_sizes) / len(order_sizes)
    stats['order_efficiency'] = {}  # items per aisle for each order
    
    # Aisle statistics  
    aisle_capacities = [sum(aisle.values()) for aisle in instance.aisles]
    stats['avg_aisle_capacity'] = sum(aisle_capacities) / len(aisle_capacities)
    
    # Item-aisle mapping for faster lookup
    stats['item_to_aisles'] = {}
    for aisle_id, aisle in enumerate(instance.aisles):
        for item_id in aisle:
            if item_id not in stats['item_to_aisles']:
                stats['item_to_aisles'][item_id] = []
            stats['item_to_aisles'][item_id].append(aisle_id)
    
    return stats

def construct_solution(instance, randomizer, stats):
    selected_orders = []
    item_totals = {}
    used_aisles = set()
    
    candidate_orders = get_viable_orders(instance, item_totals)
    
    while candidate_orders:
        order_values = []
        
        #calcula o "valor" de cada pedido
        for order_id in candidate_orders:
            value = evaluate_order(order_id, instance, item_totals, used_aisles, stats)
            if value is not None:
                order_values.append((order_id, value))
        
        if not order_values:
            break
        
        # cria o rcl (Restrict Candidate List)
        selected_order = select_from_rcl(order_values, randomizer)
        
        # atualiza os corredores e pedidos selecionados
        update_selected_aisles_items(selected_order, instance, selected_orders, item_totals, used_aisles)
        
        # termina antes se chegou no limite minimo
        if sum(item_totals.values()) >= instance.lb:
            break
        
        # valida limite maximo
        candidate_orders = [o for o in candidate_orders if o != selected_order 
                          and is_order_still_viable(o, instance, item_totals)]
    
    return Solution(selected_orders, list(used_aisles), item_totals)

def get_viable_orders(instance, current_items):
    viable = []
    current_total = sum(current_items.values())
    
    for order_id, order in enumerate(instance.orders):
        order_total = sum(order.values())
        if current_total + order_total <= instance.ub:
            viable.append(order_id)
    
    return viable

def evaluate_order(order_id, instance, item_totals, used_aisles, stats):
    order = instance.orders[order_id]
    order_total = sum(order.values())
    
    if sum(item_totals.values()) + order_total > instance.ub:
        return None
    
    # ve se nao precisa demais corredor
    new_aisles_needed = 0
    for item_id in order:
        if item_id in stats['item_to_aisles']:
            item_aisles = set(stats['item_to_aisles'][item_id])
            if not item_aisles.intersection(used_aisles):
                new_aisles_needed += len(item_aisles)

    efficiency = order_total / max(1, new_aisles_needed)
    density = order_total / len(order)  # items per item type
    
    #  retorna um valor considerando a eficiencia do item no corredor considerando sua densidade
    return 0.7 * efficiency + 0.3 * density

def select_from_rcl(order_values, randomizer):
    # Cria lista restrita de candidatos (Restrict Candidate List)
    if not order_values:
        return None
    
    best_value = order_values[0][1]
    worst_value = order_values[-1][1]
    threshold = worst_value + randomizer * (best_value - worst_value)

    #composta por todos os order_id onde o valor está acima ou igual ao threshold
    rcl = [order_id for order_id, value in order_values if value >= threshold]
    
    # Seleciona aleatoriamente da RCL
    selected_order = random.choice(rcl)
    
    return selected_order

def update_selected_aisles_items(order_id, instance, selected_orders, item_totals, used_aisles):
    selected_orders.append(order_id)
    order = instance.orders[order_id]
    
    for item_id, quantity in order.items():
        item_totals[item_id] = item_totals.get(item_id, 0) + quantity
        
        for aisle_id, aisle in enumerate(instance.aisles):
            if item_id in aisle:
                used_aisles.add(aisle_id)

def is_order_still_viable(order_id, instance, item_totals):
    order = instance.orders[order_id]
    order_total = sum(order.values())
    current_total = sum(item_totals.values())
    
    return current_total + order_total <= instance.ub

def local_search(solution, instance, stats):
    current_solution = solution
    improvement_found = True
    iteration = 0
    max_iterations = 50  # Tava entrando loop infinito nao consegui entender porque, tive que limitar iteracoes
    
    while improvement_found and iteration < max_iterations:
        improvement_found = False
        iteration += 1
        
        neighborhoods = [
            ('remove', lambda s: try_best_removal(s, instance)),
            ('add', lambda s: try_best_addition(s, instance, stats)),
            ('swap', lambda s: try_best_swap(s, instance, stats)),
        ]
        
        for name, neighborhood_func in neighborhoods:
            new_solution = neighborhood_func(current_solution)
            
            if new_solution and new_solution.evaluate() > current_solution.evaluate():
                current_solution = new_solution
                improvement_found = True
                break 
    
    return current_solution

def try_best_removal(solution, instance):
    if len(solution.order_ids) <= 1:
        return None
    
    best_solution = None
    best_score = solution.evaluate()
    
    for i in range(len(solution.order_ids)):
        candidate = try_remove_order(solution, i, instance)
        if candidate and candidate.evaluate() > best_score:
            best_solution = candidate
            best_score = candidate.evaluate()
    
    return best_solution

def try_best_addition(solution, instance, stats):
    unselected = [i for i in range(instance.n_orders) if i not in solution.order_ids]
    
    if not unselected:
        return None
    
    viable_additions = []
    current_total = sum(solution.item_totals.values())
    
    for order_id in unselected:
        order_total = sum(instance.orders[order_id].values())
        if current_total + order_total <= instance.ub:
            viable_additions.append(order_id)
    
    if not viable_additions:
        return None
    
    best_solution = None
    best_score = solution.evaluate()
    
    for order_id in viable_additions[:10]:  # limitando pra 10 pra processar mais rapido
        candidate = try_add_order(solution, order_id, instance)
        if candidate and candidate.evaluate() > best_score:
            best_solution = candidate
            best_score = candidate.evaluate()
    
    return best_solution

def try_best_swap(solution, instance, stats):
    if not solution.order_ids:
        return None
    
    unselected = [i for i in range(instance.n_orders) if i not in solution.order_ids]
    
    if not unselected:
        return None
    
    best_solution = None
    best_score = solution.evaluate()
    
    #depois de uma certa quantidade de trocas ele tava trocando com itens que ja tinha sido usado, ficou em loop
    max_swaps = min(len(solution.order_ids) * 3, 30)
    attempts = 0
    
    for i, current_order in enumerate(solution.order_ids):
        for new_order in random.sample(unselected, min(5, len(unselected))):
            candidate = try_change_order(solution, i, new_order, instance)
            if candidate and candidate.evaluate() > best_score:
                best_solution = candidate
                best_score = candidate.evaluate()
            
            attempts += 1
            if attempts >= max_swaps:
                break
        
        if attempts >= max_swaps:
            break
    
    return best_solution

def try_remove_order(solution, index, instance):
    new_order_ids = solution.order_ids.copy()
    new_order_ids.pop(index)
    
    if not new_order_ids:
        return None
    
    new_item_totals = {}
    for order_id in new_order_ids:
        for item_id, quantity in instance.orders[order_id].items():
            new_item_totals[item_id] = new_item_totals.get(item_id, 0) + quantity
    
    total_items = sum(new_item_totals.values())
    
    if total_items < instance.lb:
        return None
    
    new_aisles = calculate_required_aisles(new_item_totals, instance)
    return Solution(new_order_ids, list(new_aisles), new_item_totals)

def try_add_order(solution, new_order_id, instance):
    new_order_ids = solution.order_ids + [new_order_id]
    new_item_totals = solution.item_totals.copy()
    
    for item_id, quantity in instance.orders[new_order_id].items():
        new_item_totals[item_id] = new_item_totals.get(item_id, 0) + quantity
    
    total_items = sum(new_item_totals.values())
    
    if total_items > instance.ub:
        return None
    
    new_aisles = calculate_required_aisles(new_item_totals, instance)
    return Solution(new_order_ids, list(new_aisles), new_item_totals)

def try_change_order(solution, order_index, new_order_id, instance):
    new_order_ids = solution.order_ids.copy()
    new_order_ids[order_index] = new_order_id
    
    new_item_totals = {}
    for order_id in new_order_ids:
        for item_id, quantity in instance.orders[order_id].items():
            new_item_totals[item_id] = new_item_totals.get(item_id, 0) + quantity
    
    total_items = sum(new_item_totals.values())
    
    if total_items < instance.lb or total_items > instance.ub:
        return None
    
    new_aisles = calculate_required_aisles(new_item_totals, instance)
    return Solution(new_order_ids, list(new_aisles), new_item_totals)

def calculate_required_aisles(item_totals, instance):
    used_aisles = set()
    
    for item_id, needed_quantity in item_totals.items():
        remaining = needed_quantity
        
        for aisle_id, aisle in enumerate(instance.aisles):
            if remaining <= 0:
                break
            
            if item_id in aisle:
                used_aisles.add(aisle_id)
                remaining -= aisle[item_id]
    
    return used_aisles