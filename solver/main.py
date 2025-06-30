from instance import Instance
from grasp import grasp_solve
from utils import write_output
import sys
import os

def main():
    # pra quando eu inevitavelmente esquecer como roda o sistema
    if len(sys.argv) != 3:
        print("Use: python main.py <pasta com input> <pasta destino>")
        return
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
   
    # se output n existe, ele cria
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in sorted(os.listdir(input_folder)):
        # ignora arc q n sao txt, eh mais um failsafe dq qlqr outra coisa
        if not filename.endswith(".txt"):
            continue
            
        instance_path = os.path.join(input_folder, filename)
        print(f"Processando {filename}...")
        
        # carrega instancia
        instance = Instance.from_file(instance_path)
        
        # tenta resolver o grasp com x iteracoes, onde x tem q ser definido
        solution = grasp_solve(instance, iterations=100, randomizer=0.3, timeout=1200)
        
        # retorna resultado em um arc
        output_path = os.path.join(output_folder, filename)
        write_output(solution, output_path)
        
        print(f"Solução para {filename}: {solution.evaluate():.2f} (itens/corredor)")

if __name__ == "__main__":
    main()