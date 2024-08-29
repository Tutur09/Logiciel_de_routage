#Je sépare la partie vent du code afin de rendre le code plus compréhensible

import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.path import Path
import alphashape
from shapely.geometry import Point, MultiPoint



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
    u_interp = np.interp(lon, lon_grid[0], u[0])
    v_interp = np.interp(lat, lat_grid[:, 0], v[:, 0])

    wind_strength = np.sqrt(u_interp**2 + v_interp**2)
    wind_angle = np.rad2deg(np.arctan2(v_interp, u_interp)) % 360

    return wind_strength, wind_angle

def plot_wind_map(lon_grid, lat_grid, u, v):
    plt.figure(figsize=(10, 8))
    plt.quiver(lon_grid, lat_grid, u, v, color='blue', angles='xy', scale_units='xy', scale=10)
    plt.scatter(-122.5, 38, color='green', s=100, label='Position Initiale')
    plt.scatter(-122.5, 41, color='red', s=100, label='Position Finale')
    plt.xlim(lon_grid.min() - 0.1, lon_grid.max() + 0.1)
    plt.ylim(lat_grid.min() - 0.1, lat_grid.max() + 0.1)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Carte des Vents Simulée')
    plt.legend()
    plt.grid(True)
    plt.show()