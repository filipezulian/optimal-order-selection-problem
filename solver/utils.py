def write_output(solution, path):
    with open(path, 'w') as f:
        f.write(' '.join(map(str, sorted(solution.order_ids))) + '\n')
        f.write(' '.join(map(str, sorted(solution.aisle_ids))) + '\n')