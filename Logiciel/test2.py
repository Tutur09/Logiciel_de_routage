import random
import math
import matplotlib.pyplot as plt

# Example grid size and wind data
grid_size = (10, 10)
wind_data = [[(10, 220) for _ in range(grid_size[1])] for _ in range(grid_size[0])]

# Boat parameters
def calculate_speed(wind_speed, wind_angle, boat_heading):
    relative_angle = abs(wind_angle - boat_heading) % 360
    if relative_angle > 180:
        relative_angle = 360 - relative_angle
    if relative_angle <= 45 or relative_angle >= 135:
        return wind_speed * 0.5  # Upwind or downwind
    elif 45 < relative_angle < 135:
        return wind_speed * 0.9  # Beam reach
    return 0  # Irrelevant case

# Generate a path from a sequence of directions
def calculate_path(start, directions, wind_data, grid_size):
    path = [start]
    x, y = start
    for direction in directions:
        wind_speed, wind_angle = wind_data[int(x)][int(y)]
        speed = calculate_speed(wind_speed, wind_angle, direction) / 10
        dx = speed * math.cos(math.radians(direction))
        dy = speed * math.sin(math.radians(direction))
        x, y = max(0, min(grid_size[0] - 1, x + dx)), max(0, min(grid_size[1] - 1, y + dy))
        path.append((x, y))
    return path

# Calculate path fitness
def calculate_fitness(path, goal):
    closest_distance = min(math.sqrt((goal[0] - x) ** 2 + (goal[1] - y) ** 2) for x, y in path)
    proximity_fitness = -closest_distance
    return proximity_fitness * 10

# Genetic Algorithm components
def crossover(parent1, parent2):
    split = len(parent1) // 2
    child = parent1[:split] + parent2[split:]
    return child

def mutate(individual):
    idx = random.randint(0, len(individual) - 1)
    individual[idx] = random.uniform(0, 360)  # Replace a direction with a new random angle

# Visualization function
def plot_routes(population_paths, best_path, wind_data, grid_size, generation):
    plt.clf()
    plt.xlim(-1, grid_size[0])
    plt.ylim(-1, grid_size[1])

    # Plot wind vectors
    for x in range(grid_size[0]):
        for y in range(grid_size[1]):
            wind_speed, wind_angle = wind_data[x][y]
            dx = wind_speed * math.cos(math.radians(wind_angle))
            dy = wind_speed * math.sin(math.radians(wind_angle))
            plt.quiver(x, y, dx, dy, angles='xy', scale_units='xy', scale=10, color='blue', alpha=0.3)

    # Plot all paths in gray
    for path in population_paths:
        path_x, path_y = zip(*path)
        plt.plot(path_x, path_y, color='gray', alpha=0.5)

    # Highlight the best path in red
    if best_path:
        best_path_x, best_path_y = zip(*best_path)
        plt.plot(best_path_x, best_path_y, color='red', linewidth=2, label='Best Path')

    plt.title(f"Generation {generation} - All Paths")
    plt.legend()
    plt.pause(0.1)  # Pause to update the plot

# Genetic Algorithm with live visualization
def genetic_algorithm(start, goal, wind_data, grid_size, population_size, generations, max_steps):
    print("Starting Genetic Algorithm...")
    population = [[random.uniform(0, 360) for _ in range(max_steps)] for _ in range(population_size)]
    best_individual = None
    best_fitness = float('-inf')

    plt.figure(figsize=(10, 10))
    for gen in range(generations):
        print(f"Generation {gen+1}")
        fitness_scores = []
        population_paths = []

        for individual in population:
            path = calculate_path(start, individual, wind_data, grid_size)
            population_paths.append(path)
            fitness = calculate_fitness(path, goal)
            fitness_scores.append(fitness)

        # Sort population by fitness (descending order)
        population = [ind for _, ind in sorted(zip(fitness_scores, population), reverse=True)]
        population_paths = [path for _, path in sorted(zip(fitness_scores, population_paths), reverse=True)]
        fitness_scores.sort(reverse=True)

        # Keep the best individual
        if fitness_scores[0] > best_fitness:
            best_fitness = fitness_scores[0]
            best_individual = population[0]

        # Plot all paths and highlight the best path
        best_path = calculate_path(start, best_individual, wind_data, grid_size)
        plot_routes(population_paths, best_path, wind_data, grid_size, gen + 1)

        # Create the next generation
        next_generation = population[:10]  # Keep top 10 individuals (elitism)
        while len(next_generation) < population_size:
            parent1, parent2 = random.choices(population[:50], k=2)  # Select from the top 50
            child = crossover(parent1, parent2)
            if random.random() < 0.1:  # 10% mutation rate
                mutate(child)
            next_generation.append(child)
        population = next_generation

    plt.show()
    return best_individual, best_fitness

# Example usage
start = (0, 0)
goal = (9, 9)
population_size = 100
generations = 50
max_steps = 20

best_directions, best_fitness = genetic_algorithm(start, goal, wind_data, grid_size, population_size, generations, max_steps)
best_path = calculate_path(start, best_directions, wind_data, grid_size)
print("Best Directions:", best_directions)
print("Best Path:", best_path)
print("Best Fitness:", best_fitness)