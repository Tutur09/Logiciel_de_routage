#Je sépare la partie vent du code afin de rendre le code plus compréhensible
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.path import Path
import alphashape
from shapely.geometry import Point, MultiPoint
from scipy.interpolate import griddata
from scipy.spatial import cKDTree

from cartopy import crs as ccrs, feature as cfeature
from time import time
import xarray as xr
import os

file_path = 'C:/Users/arthu/OneDrive/Arthur/Programmation/TIPE_Arthur_Lhoste/Logiciel/Données_vent/METEOCONSULT12Z_VENT_0921_Gascogne.grb'
# Charge le dataset
ds = xr.open_dataset(file_path, engine='cfgrib')

# Charger les données u10 et v10 pour tout le dataset comme ça pas besoin de recalculer
ds.u10.load()
ds.v10.load()

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
    start = time()
    u_interp = griddata(points, u_values, (lon, lat), method='linear')
    v_interp = griddata(points, v_values, (lon, lat), method='linear')
    stop = time()
    print("temps interpolation ", stop - start)

    if u_interp is None or v_interp is None:
        raise ValueError("La position demandée est en dehors des limites de la grille.")

    # Calcul de la force du vent et de la direction
    wind_strength = np.sqrt(u_interp**2 + v_interp**2)
    wind_angle = (np.rad2deg(np.arctan2(v_interp, u_interp))-90) % 360

    return wind_strength, wind_angle

def plot_wind_map(lon_grid, lat_grid, u, v, pos_i, pos_f, chemin_x=None, chemin_y=None):
    projPC = ccrs.PlateCarree()  # Projection Plate Carree
    
    # Définir les limites géographiques
    lonW = lon_grid.min()
    lonE = lon_grid.max()
    latS = lat_grid.min()
    latN = lat_grid.max()
    
    # Création de la figure avec projection géographique
    fig = plt.figure(figsize=(10, 8))
    ax = plt.subplot(1, 1, 1, projection=projPC)
    ax.set_title('Carte des Vents avec Chemin Idéal et Interpolation')

    # Tracé de la carte avec les frontières
    ax.set_extent([lonW, lonE, latS, latN], crs=projPC)
    ax.coastlines(resolution='110m', color='black')
    ax.add_feature(cfeature.STATES, linewidth=0.5, edgecolor='brown')
    ax.add_feature(cfeature.BORDERS, linewidth=0.7, edgecolor='blue')
    
    # Affichage du quadrillage
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')

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
    contour = ax.contourf(lon_interp, lat_interp, wind_magnitude_interp, cmap=cmap, levels=100, norm=norm, transform=ccrs.PlateCarree())

    # Affichage du champ de vent avec des flèches noires (taille ajustée)
    ax.quiver(lon_grid, lat_grid, u, v, color='black', angles='xy', scale_units='xy', scale=200, transform=ccrs.PlateCarree())

    # Affichage des points de départ et d'arrivée
    ax.scatter(pos_i[0], pos_i[1], color='green', s=100, label='Position Initiale', transform=ccrs.PlateCarree())
    ax.scatter(pos_f[0], pos_f[1], color='red', s=100, label='Position Finale', transform=ccrs.PlateCarree())

    # Tracé du chemin idéal s'il est fourni
    if chemin_x is not None and chemin_y is not None:
        ax.plot(chemin_x, chemin_y, color='black', linestyle='-', linewidth=2, label='Chemin Idéal', transform=ccrs.PlateCarree())
        ax.scatter(chemin_x, chemin_y, color='black', s=50, transform=ccrs.PlateCarree())

    # Ajout de la barre de couleur
    cbar = plt.colorbar(contour, ax=ax, orientation='vertical', label='Force du vent')

    # Affichage de la légende et du quadrillage
    ax.legend()
    plt.show()

def plot_wind(step_indices=[1], chemin_x=None, chemin_y=None, skip=4, save_plots=False, output_dir=r'C:\Users\arthu\OneDrive\Arthur\Programmation\TIPE_Arthur_Lhoste\images_png'):
    # Créer une figure pour les plots
    for step_index in step_indices:
        plt.figure(figsize=(12, 7))  # Créer une nouvelle figure à chaque étape

        # Choisir une étape spécifique
        u10_specific = ds['u10'].isel(step=step_index)
        v10_specific = ds['v10'].isel(step=step_index)

        # Calculer la vitesse du vent
        wind_speed = np.sqrt(u10_specific**2 + v10_specific**2)

        # Créer un sous-plot pour chaque étape
        ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.set_extent([-10, -1, 43.2, 49], crs=ccrs.PlateCarree())  # Ajuste ces valeurs en fonction de ta zone d'intérêt

        # Ajouter des features de la carte
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAND, facecolor='lightgray')
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

        # Tracer la grille de latitudes et longitudes
        gl = ax.gridlines(draw_labels=True, color='gray', alpha=0.5, linestyle='--')
        gl.top_labels = False  # Désactive les labels en haut
        gl.right_labels = False  # Désactive les labels à droite
        gl.xlabel_style = {'size': 10}  # Taille du texte pour les longitudes
        gl.ylabel_style = {'size': 10}  # Taille du texte pour les latitudes

        # Tracer les vecteurs de vent avec un échantillonnage, en fonction des latitudes et longitudes
        q = ax.quiver(ds['longitude'][::skip], ds['latitude'][::skip], 
                      u10_specific[::skip, ::skip], v10_specific[::skip, ::skip], 
                      wind_speed[::skip, ::skip], scale=50, cmap='viridis', 
                      transform=ccrs.PlateCarree())

        # Ajouter les titres et les étiquettes
        ax.set_title(f"Carte des vents - Étape {step_index}")
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        # Ajouter une légende pour la vitesse du vent
        plt.colorbar(q, ax=ax, label='Vitesse du vent (m/s)', orientation='vertical')

        # Tracé du chemin idéal s'il est fourni
        if chemin_x is not None and chemin_y is not None:
            ax.plot(chemin_x, chemin_y, color='black', linestyle='-', linewidth=2, label='Chemin Idéal', transform=ccrs.PlateCarree())
            ax.scatter(chemin_x, chemin_y, color='black', s=50, label='Points du Chemin', transform=ccrs.PlateCarree())

        # Enregistrer le plot si l'option save_plots est activée
        if save_plots:
            plot_filename = f"{output_dir}/carte_vents_step_{step_index}.png"
            plt.savefig(plot_filename)
            print(f"Plot enregistré sous : {plot_filename}")

        plt.tight_layout()
         # Montrer les plots seulement si save_plots est False
        if not save_plots:
            plt.show()  # Afficher les plots
        



def get_wind_from_grib(lat, lon, time_step=0):
    """
    Récupère les composantes u10 et v10 du vent à partir du voisin le plus proche.
    """
    lon = lon % 360
    start = time()
    
    # Maintenant, l'accès aux données sera plus rapide
    u10_values = ds.u10.isel(step=time_step).values
    v10_values = ds.v10.isel(step=time_step).values
    stop1 = time()
    #print(stop1 - start)
    
    latitudes = ds.latitude.values
    longitudes = ds.longitude.values
    
    stop = time()
    #print('temps récupérer une fois le vent ', stop - start)
    
    # Trouver le voisin le plus proche
    lat_diff = np.abs(latitudes - lat)
    lon_diff = np.abs(longitudes - lon)
       
    # Calculer les distances
    distances = lat_diff[:, None]**2 + lon_diff**2  # Matrice des distances
    closest_index = np.unravel_index(np.argmin(distances), distances.shape)
    
    
    # Récupérer les valeurs du voisin le plus proche
    u10 = u10_values[closest_index]
    v10 = v10_values[closest_index]
    
    # Calculer la vitesse et l'angle
    v_vent = np.sqrt((u10)**2 + v10**2) 
    a_vent = (np.degrees(np.arctan2(-u10, -v10))) % 360 
    
    
    return v_vent, a_vent

def enregistrement_route(chemin_x, chemin_y, heures, output_dir='./', skip = 4):
    
    # Créer le répertoire de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for heure in range(0, heures, 3):
        plt.figure(figsize=(12, 7))

        # Choisir les données de vent pour l'heure actuelle
        u10_specific = ds['u10'].isel(step=heure)
        v10_specific = ds['v10'].isel(step=heure)
        wind_speed = np.sqrt(u10_specific**2 + v10_specific**2)

        # Créer un sous-plot
        ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.set_extent([-10, -1, 43.2, 49], crs=ccrs.PlateCarree())

        # Ajouter des features de la carte
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAND, facecolor='lightgray')
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

        # Tracer la route idéale jusqu'à l'heure actuelle
        ax.plot(chemin_x[:heure + 1], chemin_y[:heure + 1], color='black', linestyle='-', linewidth=2, label='Chemin Idéal', transform=ccrs.PlateCarree())
        ax.scatter(chemin_x[:heure + 1], chemin_y[:heure + 1], color='black', s=50, transform=ccrs.PlateCarree())

        # Tracer les vecteurs de vent
        q = ax.quiver(ds['longitude'][::skip], ds['latitude'][::skip], 
                      u10_specific[::skip, ::skip], v10_specific[::skip, ::skip], 
                      wind_speed[::skip, ::skip], scale=50, cmap='viridis', 
                      transform=ccrs.PlateCarree())

        # Ajouter les titres et les étiquettes
        ax.set_title(f"Route Idéale et Vent à l'Heure {heure}")
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        # Ajouter une légende pour la vitesse du vent
        plt.colorbar(q, ax=ax, label='Vitesse du vent (m/s)', orientation='vertical')

        # Enregistrer le plot
        plot_filename = f"{output_dir}/route_ideale_vent_heure_{heure}.png"
        plt.savefig(plot_filename)
        print(f"Plot enregistré sous : {plot_filename}")

        plt.close()  # Fermer la figure pour libérer la mémoire
    


# # Exemple d'utilisation
lon = -3.0  # Longitude de la position
lat = 47.0  # Latitude de la position
lon1 = -4.468
lat1 = 47.29
# step_index = 10  # Index de l'étape

# start = time()
# wind_strength, wind_angle = get_wind_from_grib(lon, lat)
# stop = time()
# print('temps est de ', stop - start)
# print("Force du vent :", wind_strength)
# print("Direction du vent :", wind_angle)
#plot_wind(step_indices=[i for i in range(120)], save_plots=True)

print(ds)

print('**************** valid time **************** \n ', ds.valid_time.values)