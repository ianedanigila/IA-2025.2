import random
import heapq
from collections import deque

# ---------------------------------------
# Fixed initial puzzle configuration 
INITIAL_STATE = [1, 7, 8,
                 3, 5, 0,
                 6, 4, 2]
USE_INITIAL_STATE = True
# ---------------------------------------

# Goal state of the 8-puzzle
GOAL_STATE = [1, 2, 3, 4, 5, 6, 7, 8, 0]

# GA Parameters 
MAX_NODES_TO_EXPLORE = 500000 # Limite para evitar loop infinito

# Toggle to use Manhattan distance 
USE_MANHATTAN = True

# Map each tile to its goal (row, col) position 
GOAL_POSITIONS = {value: (i // 3, i % 3) for i, value in enumerate(GOAL_STATE)}

class Node:
    def __init__(self, state, parent=None, action=None, g=0):
        # Estado (tupla para ser imutável)
        self.state = tuple(state) 
        # Custo real do caminho (g(n))
        self.g = g 
        # Custo heurístico (h(n) - Distância de Manhattan)
        self.h = fitness_manhattan(self.state) 
        # Custo total (f(n) = g(n) + h(n))
        self.f = self.g + self.h
        
        # Histórico para reconstrução do caminho
        self.parent = parent
        self.action = action

    # Sobrescreve a comparação: prioriza o menor f(n)
    def __lt__(self, other):
        return self.f < other.f
# -----------------------------------------------

# Fitness function: misplaced tiles 
def fitness_misplaced(state):
    # Converte para lista para usar no sum, se necessário
    state_list = list(state)
    return sum([1 for i in range(9) if state_list[i] != GOAL_STATE[i]])

# Fitness function: Manhattan distance 
def fitness_manhattan(state):
    distance = 0
    # Converte para lista para usar no enumerate, se necessário
    state_list = list(state)
    for i, tile in enumerate(state_list):
        if tile == 0:
            continue
        curr_row, curr_col = i // 3, i % 3
        goal_row, goal_col = GOAL_POSITIONS[tile]
        distance += abs(curr_row - goal_row) + abs(curr_col - goal_col)
    return distance

# Unified fitness selector 
def heuristic(state):
    return fitness_manhattan(state) if USE_MANHATTAN else fitness_misplaced(state)

# Check if a puzzle is solvable 
def is_solvable(puzzle):
    inv_count = sum(
        1 for i in range(8) for j in range(i + 1, 9)
        if puzzle[i] and puzzle[j] and puzzle[i] > puzzle[j]
    )
    return inv_count % 2 == 0

def get_neighbors(state_list):
    state = state_list
    zero_index = state.index(0)
    zero_row, zero_col = zero_index // 3, zero_index % 3
    
    neighbors = []
    moves = {'Up': (-1, 0), 'Down': (1, 0), 'Left': (0, -1), 'Right': (0, 1)}
    
    for action, (dr, dc) in moves.items():
        new_row, new_col = zero_row + dr, zero_col + dc
        
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_index = new_row * 3 + new_col
            new_state = list(state)
            
            # Trocar o 0 com a peça vizinha
            new_state[zero_index], new_state[new_index] = new_state[new_index], new_state[zero_index]
            
            neighbors.append((tuple(new_state), action))

    return neighbors
# ----------------------------------------------------

def reconstruct_path(goal_node):
    path = []
    current = goal_node
    while current.parent:
        path.append(current.action)
        current = current.parent
    path.reverse()
    return path
# -----------------------------------------------

# Loop principal do A* (Substituindo o Loop GA)
def solve_a_star():
    if not is_solvable(INITIAL_STATE):
        print("ERROR: The initial state is not solvable!")
        return None

    # 1. Inicializa o nó raiz
    initial_node = Node(INITIAL_STATE, g=0)
    
    # 2. Open List (Fila de Prioridade - Heap)
    open_list = [initial_node]
    
    # 3. Closed Set (Set de estados visitados para evitar ciclos e pior caminho)
    # Armazena {estado_tupla: custo_g}
    closed_set = {initial_node.state: initial_node.g} 
    
    GOAL_STATE_TUPLE = tuple(GOAL_STATE)
    
    print(f"Estado Inicial: {INITIAL_STATE} | Distância Manhattan (h): {initial_node.h}")
    
    nodes_explored = 0
    
    while open_list and nodes_explored < MAX_NODES_TO_EXPLORE:
        current_node = heapq.heappop(open_list)
        nodes_explored += 1
                
        # Condição de parada (Goal Check)
        if current_node.state == GOAL_STATE_TUPLE:
            print("\nGoal reached! (Caminho Otimizado encontrado)")
            print(f"Nodes Explorados: {nodes_explored}")
            return current_node

        # Expansão
        for neighbor_state, action in get_neighbors(list(current_node.state)):
            new_g = current_node.g + 1 # Custo g(n) = Custo anterior + 1 movimento

            # Se o vizinho já foi visitado E o novo caminho não é mais curto, ignore
            if neighbor_state in closed_set and new_g >= closed_set[neighbor_state]:
                continue
                
            # Este é um novo estado OU é um caminho mais curto
            neighbor_node = Node(
                state=neighbor_state,
                parent=current_node,
                action=action,
                g=new_g
            )
            
            # Adiciona/Atualiza o estado e adiciona à Open List
            closed_set[neighbor_state] = new_g
            heapq.heappush(open_list, neighbor_node)

    print("\nLimite de nós explorados atingido ou busca falhou.")
    return None

# Run the A*
if __name__ == "__main__":
    print("=== Algoritmo A* para 8-Puzzle (Fine-Tuning do Caminho) ===")
    print(f"Usando Distância Manhattan como heurístico: {USE_MANHATTAN}\n")

    goal_node = solve_a_star()

    if goal_node:
        solution_path = reconstruct_path(goal_node)
        print(f"\nNúmero Mínimo de Movimentos (Custo g(n)): {goal_node.g}")
        print("Caminho Otimizado (Sequência de Movimentos):")
        print(solution_path)