import random
import math
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import numpy as np

# Chargement des données de vent depuis un fichier GRIB
def load_wind_data(file_path):
    ds = xr.open_dataset(file_path, engine='cfgrib')
    u10 = ds.u10.isel(step=int(0)).values
    v10 = ds.v10.isel(step=int(0)).values

    # Vérifiez les dimensions des données
    print(f"u10 dimensions: {u10.shape}, v10 dimensions: {v10.shape}")

    # Assurez-vous que u10 et v10 sont bien 2D
    if len(u10.shape) > 2:
        raise ValueError("Les données GRIB contiennent des dimensions supplémentaires non prises en charge.")

    # Calcul de la vitesse et de la direction du vent
    speed = np.sqrt(u10**2 + v10**2)
    direction = (np.arctan2(v10, u10) * 180 / np.pi + 360) % 360

    grid_size = (u10.shape[0], u10.shape[1])
    # Convertir en tuples de scalaires
    wind_data = [[(speed[i, j].item(), direction[i, j].item()) for j in range(grid_size[1])] for i in range(grid_size[0])]
    return wind_data, grid_size


def calculate_speed(wind_speed, wind_angle, boat_heading):
    # S'assurer que les valeurs sont scalaires
    wind_speed = float(wind_speed)
    wind_angle = float(wind_angle)
    boat_heading = float(boat_heading)

    relative_angle = abs(wind_angle - boat_heading) % 360
    if relative_angle > 180:
        relative_angle = 360 - relative_angle
    if relative_angle <= 45 or relative_angle >= 135:
        return wind_speed * 0.5  # Upwind ou downwind
    elif 45 < relative_angle < 135:
        return wind_speed * 0.9  # Beam reach
    return 0  # Cas hors de portée


def calculate_path(start, directions, wind_data, grid_size):
    path = [start]
    x, y = start
    for direction in directions:
        wind_speed, wind_angle = wind_data[int(x)][int(y)]
        wind_speed = float(wind_speed)  # Convertion explicite en scalaire
        wind_angle = float(wind_angle)

        speed = calculate_speed(wind_speed, wind_angle, direction) / 10
        dx = speed * math.cos(math.radians(direction))
        dy = speed * math.sin(math.radians(direction))
        x, y = max(0, min(grid_size[0] - 1, x + dx)), max(0, min(grid_size[1] - 1, y + dy))
        path.append((x, y))
    return path



# Calcul de la fitness d'un chemin
def calculate_fitness(path, goal):
    closest_distance = min(math.sqrt((goal[0] - x) ** 2 + (goal[1] - y) ** 2) for x, y in path)
    proximity_fitness = -closest_distance
    return proximity_fitness * 10

# Crossover pour l'algorithme génétique
def crossover(parent1, parent2):
    split = len(parent1) // 2
    child = parent1[:split] + parent2[split:]
    return child

# Mutation pour l'algorithme génétique
def mutate(individual):
    idx = random.randint(0, len(individual) - 1)
    individual[idx] = random.uniform(0, 360)  # Remplace une direction par un nouvel angle aléatoire

# Visualisation des routes
def plot_routes(population_paths, best_path, wind_data, grid_size, generation):
    plt.clf()
    plt.xlim(-1, grid_size[0])
    plt.ylim(-1, grid_size[1])

    # Affiche les vecteurs de vent
    for x in range(grid_size[0]):
        for y in range(grid_size[1]):
            wind_speed, wind_angle = wind_data[x][y]
            dx = wind_speed * math.cos(math.radians(wind_angle))
            dy = wind_speed * math.sin(math.radians(wind_angle))
            plt.quiver(x, y, dx, dy, angles='xy', scale_units='xy', scale=10, color='blue', alpha=0.3)

    # Affiche tous les chemins en gris
    for path in population_paths:
        path_x, path_y = zip(*path)
        plt.plot(path_x, path_y, color='gray', alpha=0.5)

    # Met en évidence le meilleur chemin en rouge
    if best_path:
        best_path_x, best_path_y = zip(*best_path)
        plt.plot(best_path_x, best_path_y, color='red', linewidth=2, label='Best Path')

    plt.title(f"Generation {generation} - All Paths")
    plt.legend()
    plt.pause(0.1)  # Pause pour mettre à jour le graphique

# Algorithme génétique avec visualisation en direct
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

        # Trier la population par fitness (ordre décroissant)
        population = [ind for _, ind in sorted(zip(fitness_scores, population), reverse=True)]
        population_paths = [path for _, path in sorted(zip(fitness_scores, population_paths), reverse=True)]
        fitness_scores.sort(reverse=True)

        # Conserver le meilleur individu
        if fitness_scores[0] > best_fitness:
            best_fitness = fitness_scores[0]
            best_individual = population[0]

        # Afficher tous les chemins et mettre en évidence le meilleur
        best_path = calculate_path(start, best_individual, wind_data, grid_size)
        plot_routes(population_paths, best_path, wind_data, grid_size, gen + 1)

        # Créer la prochaine génération
        next_generation = population[:10]  # Conserver les 10 meilleurs individus (élitisme)
        while len(next_generation) < population_size:
            parent1, parent2 = random.choices(population[:50], k=2)  # Sélectionner parmi les 50 meilleurs
            child = crossover(parent1, parent2)
            if random.random() < 0.1:  # Taux de mutation de 10%
                mutate(child)
            next_generation.append(child)
        population = next_generation

    plt.show()
    return best_individual, best_fitness

# Exemple d'exécution
file_path = r'Logiciel\Données_vent\METEOCONSULT12Z_VENT_1208_Nord_Atlantique.grb'
wind_data, grid_size = load_wind_data(file_path)

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
