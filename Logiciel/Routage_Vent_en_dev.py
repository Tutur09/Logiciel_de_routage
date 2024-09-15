#Je sépare la partie vent du code afin de rendre le code plus compréhensible

import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.path import Path
import alphashape
from shapely.geometry import Point, MultiPoint

from scipy.interpolate import griddata





def generate_wind_map(lon_min, lon_max, lat_min, lat_max, grid_size, wind_strength_range, wind_angle_range):

    lon = np.linspace(lon_min, lon_max, grid_size)
    lat = np.linspace(lat_min, lat_max, grid_size)
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    wind_strength = np.random.uniform(wind_strength_range[0], wind_strength_range[1], size=(grid_size, grid_size))
    wind_angle = np.random.uniform(wind_angle_range[0], wind_angle_range[1], size=(grid_size, grid_size))

    wind_angle_rad = np.deg2rad(wind_angle)

    u = wind_strength * np.cos(wind_angle_rad)
    v = wind_strength * np.sin(wind_angle_rad)

    return lon_grid, lat_grid, u, v

def excel2wind_map():
    fichier = r"C:\Users\arthu\OneDrive\Arthur\Programmation\TIPE_Arthur_Lhoste\Logiciel\Vent.xlsx"
    data = pd.read_excel(fichier, header=None)
    
    # Lire les paramètres de latitude, longitude et taille de grille
    lat_i, lon_i, grid_size = data.iloc[1, 0], data.iloc[1, 1], data.iloc[1, 2]
    nb_col, nb_lig = data.shape[1] - 1, data.shape[0] - 4
    
    # Déterminer les limites de latitude et longitude
    lat_max = lat_i - grid_size * nb_lig
    lon_max = lon_i + grid_size * nb_col
    lat_min = lat_i
    lon_min = lon_i
    
    # Lire les valeurs de vent depuis le tableau Excel
    u_values = []
    v_values = []
    
    for i in range(nb_lig):
        u_row = []
        v_row = []
        for j in range(0, nb_col):
            # Lire la cellule et diviser les valeurs
            u_v = data.iloc[4 + nb_lig - 1 - i, j + 1].split(';')
            u_row.append(float(u_v[0]))  # Composante u
            v_row.append(float(u_v[1]))  # Composante v
        u_values.append(u_row)
        v_values.append(v_row)
    
    u_values = np.array(u_values)
    v_values = np.array(v_values)

    # Créer les grilles de coordonnées (longitude et latitude)
    lon_grid, lat_grid = np.meshgrid(
        np.linspace(lon_min, lon_max, u_values.shape[1]),
        np.linspace(lat_max, lat_min, u_values.shape[0])
    )

    return lon_grid, lat_grid, u_values, v_values

#print(excel2wind_map())


def get_wind_at_position(lon, lat, lon_grid, lat_grid, u, v):
    """
    Interpoler la direction et la force du vent à une position donnée.

    Args:
         lon (float): Longitude de la position.
         lat (float): Latitude de la position.
         lon_grid (ndarray): Coordonnées de longitude de la grille.
         lat_grid (ndarray): Coordonnées de latitude de la grille.
         u (ndarray): Composante u des vecteurs de vent.
         v (ndarray): Composante v des vecteurs de vent.

    Returns:
        tuple: Force du vent et direction du vent en degrés.
    """
    # Aplatir les grilles et les composants pour l'interpolation
    points = np.array([lon_grid.flatten(), lat_grid.flatten()]).T
    u_values = u.flatten()
    v_values = v.flatten()
    
    # Interpolation des composants de vent
    u_interp = griddata(points, u_values, (lon, lat), method='linear')
    v_interp = griddata(points, v_values, (lon, lat), method='linear')

    if u_interp is None or v_interp is None:
        raise ValueError("La position demandée est en dehors des limites de la grille.")

    # Calcul de la force du vent et de la direction
    wind_strength = np.sqrt(u_interp**2 + v_interp**2)
    wind_angle = (np.rad2deg(np.arctan2(v_interp, u_interp))-90) % 360

    return wind_strength, wind_angle


def plot_wind_map(lon_grid, lat_grid, u, v, pos_i, pos_f, chemin_x=None, chemin_y=None):
    plt.figure(figsize=(10, 8))
    
    # Calcul de la magnitude du vent
    wind_magnitude = np.sqrt(u**2 + v**2)
    
    # Création d'une grille régulière pour l'interpolation
    lon_lin = np.linspace(lon_grid.min(), lon_grid.max(), 300)
    lat_lin = np.linspace(lat_grid.min(), lat_grid.max(), 300)
    lon_interp, lat_interp = np.meshgrid(lon_lin, lat_lin)
    
    # Interpolation des composantes u et v sur la nouvelle grille
    u_interp = griddata((lon_grid.ravel(), lat_grid.ravel()), u.ravel(), (lon_interp, lat_interp), method='cubic')
    v_interp = griddata((lon_grid.ravel(), lat_grid.ravel()), v.ravel(), (lon_interp, lat_interp), method='cubic')
    
    # Calcul de la magnitude du vent interpolé
    wind_magnitude_interp = np.sqrt(u_interp**2 + v_interp**2)
    
    # Utilisation de la colormap pour la vitesse du vent
    cmap = plt.get_cmap('viridis')
    
    # Normalisation des couleurs par rapport à la magnitude du vent interpolé
    norm = plt.Normalize(wind_magnitude_interp.min(), wind_magnitude_interp.max())
    
    # Affichage de la carte colorée avec les magnitudes du vent interpolées
    plt.contourf(lon_interp, lat_interp, wind_magnitude_interp, cmap=cmap, levels=100, norm=norm)
    
    # Affichage du champ de vent avec des flèches noires (taille ajustée)
    plt.quiver(lon_grid, lat_grid, -u, -v, color='black', angles='xy', scale_units='xy', scale=50)
    
    # Affichage des points de départ et d'arrivée
    plt.scatter(pos_i[0], pos_i[1], color='green', s=100, label='Position Initiale')
    plt.scatter(pos_f[0], pos_f[1], color='red', s=100, label='Position Finale')
    
    # Tracé du chemin idéal s'il est fourni
    if chemin_x is not None and chemin_y is not None:
        plt.plot(chemin_x, chemin_y, color='black', linestyle='-', linewidth=2, label='Chemin Idéal')
        plt.scatter(chemin_x, chemin_y, color='black', s=50)
    
    # Paramètres du graphique
    plt.xlim(lon_grid.min() - 0.1, lon_grid.max() + 0.1)
    plt.ylim(lat_grid.min() - 0.1, lat_grid.max() + 0.1)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Carte des Vents avec Chemin Idéal et Interpolation')
    
    # Ajout de la barre de couleur
    plt.colorbar(label='Force du vent')
    
    plt.legend()
    plt.grid(True)
    plt.show()




lon_grid, lat_grid, u_values, v_values = excel2wind_map()

position_initiale = (8, 43)
position_finale = (8, 49)

#print(get_wind_at_position(6,46, lon_grid, lat_grid, u_values, v_values))

#print(get_wind_at_position(3,46, lon_grid, lat_grid, u_values, v_values))

plot_wind_map(lon_grid, lat_grid, u_values, v_values, position_initiale, position_finale)
