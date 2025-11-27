import random

# ---------------------------------------
# Fixed initial puzzle configuration
# (Set this to whatever valid puzzle you want)
# 0 = empty tile
INITIAL_STATE = [1, 7, 8,
                 3, 5, 0,
                 6, 4, 2]

# Toggle  to use the fixed initial puzzle
USE_INITIAL_STATE = True
# ---------------------------------------

# Goal state of the 8-puzzle
GOAL_STATE = [1, 2, 3, 4, 5, 6, 7, 8, 0]

# GA Parameters
POPULATION_SIZE = 200
MUTATION_RATE = 0.15
MAX_GENERATIONS = 1000
TOURNAMENT_SIZE = 7

# Toggle to use Manhattan distance instead of misplaced tiles
USE_MANHATTAN = True

# Map each tile to its goal (row, col) position for Manhattan distance
GOAL_POSITIONS = {value: (i // 3, i % 3) for i, value in enumerate(GOAL_STATE)}

# Fitness function: misplaced tiles
def fitness_misplaced(state):
    return sum([1 for i in range(9) if state[i] != GOAL_STATE[i]])

# Fitness function: Manhattan distance
def fitness_manhattan(state):
    distance = 0
    for i, tile in enumerate(state):
        if tile == 0:
            continue
        curr_row, curr_col = i // 3, i % 3
        goal_row, goal_col = GOAL_POSITIONS[tile]
        distance += abs(curr_row - goal_row) + abs(curr_col - goal_col)
    return distance

# Unified fitness selector
def fitness(state):
    return fitness_manhattan(state) if USE_MANHATTAN else fitness_misplaced(state)

# Generate a random valid 8-puzzle individual
def generate_individual():
    state = list(range(9))
    while True:
        random.shuffle(state)
        if is_solvable(state):
            return state

# Check if a puzzle is solvable
def is_solvable(puzzle):
    inv_count = sum(
        1 for i in range(8) for j in range(i + 1, 9)
        if puzzle[i] and puzzle[j] and puzzle[i] > puzzle[j]
    )
    return inv_count % 2 == 0

# Tournament selection
def select_parents(population):
    tournament = random.sample(population, TOURNAMENT_SIZE)
    tournament.sort(key=fitness)
    return tournament[0], tournament[1]

# Crossover: ordered crossover for permutation encoding
def crossover(parent1, parent2):
    point = random.randint(1, 7)
    child = parent1[:point]
    for gene in parent2:
        if gene not in child:
            child.append(gene)
    return child

# Mutation: swap two tiles
def mutate(individual):
    if random.random() < MUTATION_RATE:
        i, j = random.sample(range(9), 2)
        individual[i], individual[j] = individual[j], individual[i]

# Main GA loop
def genetic_algorithm():
    population = []

    # If enabled, manually place the initial puzzle in the population
    if USE_INITIAL_STATE:
        if not is_solvable(INITIAL_STATE):
            print("ERROR: The initial state is not solvable!")
            return None

        population.append(INITIAL_STATE.copy())  # Add your fixed initial state

        # Fill the rest of the population with random valid puzzles
        while len(population) < POPULATION_SIZE:
            population.append(generate_individual())
    else:
        # Full random population
        population = [generate_individual() for _ in range(POPULATION_SIZE)]

    # Evolution loop
    for generation in range(MAX_GENERATIONS):
        population.sort(key=fitness)
        best = population[0]
        print(f"Generation {generation} | Best fitness: {fitness(best)} | State: {best}")

        if fitness(best) == 0:
            print("Goal reached!")
            return best

        new_population = []
        while len(new_population) < POPULATION_SIZE:
            parent1, parent2 = select_parents(population)
            child = crossover(parent1, parent2)
            mutate(child)
            new_population.append(child)

        population = new_population

    print("Goal not reached within the generation limit.")
    return None

# Run the GA
if __name__ == "__main__":
    print("=== Genetic Algorithm for 8-Puzzle ===")
    print(f"Using Manhattan Distance: {USE_MANHATTAN}")
    print(f"Using predefined initial state: {USE_INITIAL_STATE}\n")

    solution = genetic_algorithm()

    if solution:
        print("\nFinal solution:", solution)