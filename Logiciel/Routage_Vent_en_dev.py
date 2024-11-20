#Je sépare la partie vent du code afin de rendre le code plus compréhensible
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from time import time
import os

from scipy.interpolate import griddata

from cartopy import crs as ccrs, feature as cfeature

from shapely.ops import nearest_points
from geopy.distance import geodesic



import geopandas as gpd
import xarray as xr

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

    # Création des grilles de coordonnées (longitude et latitude)
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

def plot_wind(loc, step_indices=[1], chemin_x=None, chemin_y=None, skip=4, save_plots=False, output_dir=r'C:\Users\arthu\OneDrive\Arthur\Programmation\TIPE_Arthur_Lhoste\images_png'):
    # Créer une figure pour chaque étape spécifiée dans step_indices
    for step_index in step_indices:
        plt.figure(figsize=(12, 7))  # Créer une nouvelle figure à chaque étape

        # Choisir une étape spécifique dans les données de vent
        u10_specific = ds['u10'].isel(step=int(step_index))
        v10_specific = ds['v10'].isel(step=int(step_index))

        # Calculer la vitesse du vent pour chaque point
        wind_speed = np.sqrt(u10_specific**2 + v10_specific**2)

        # Création du sous-plot avec une projection cartographique et un fond de carte à résolution de 50 m
        ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.set_extent(loc, crs=ccrs.PlateCarree())  # Zone d'intérêt avec haute précision

        # Ajouter les éléments de carte à résolution de 50 m
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=1)
        ax.add_feature(cfeature.BORDERS.with_scale('50m'), linestyle=':')
        ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='lightgray')
        ax.add_feature(cfeature.OCEAN.with_scale('50m'), facecolor='lightblue')

        # Tracer la grille de latitude et de longitude
        gl = ax.gridlines(draw_labels=True, color='gray', alpha=0.5, linestyle='--')
        gl.top_labels = False  # Désactive les labels en haut
        gl.right_labels = False  # Désactive les labels à droite
        gl.xlabel_style = {'size': 10} 
        gl.ylabel_style = {'size': 10}  

        # Tracer les vecteurs de vent (u, v) avec un échantillonnage `skip` pour une meilleure lisibilité
        q = ax.quiver(ds['longitude'][::skip], ds['latitude'][::skip], 
                      u10_specific[::skip, ::skip], v10_specific[::skip, ::skip], 
                      wind_speed[::skip, ::skip], scale=30, cmap='viridis', 
                      transform=ccrs.PlateCarree())

        # Ajouter un titre et des étiquettes
        ax.set_title(f"Carte des vents - Étape {step_index}")
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        # Ajouter une légende pour la vitesse du vent
        plt.colorbar(q, ax=ax, label='Vitesse du vent (m/s)', orientation='vertical')

        # Tracé du chemin idéal s'il est fourni
        if chemin_x is not None and chemin_y is not None:
            ax.plot(chemin_x, chemin_y, color='black', linestyle='-', linewidth=2, label='Chemin Idéal', transform=ccrs.PlateCarree())
            ax.scatter(chemin_x, chemin_y, color='black', s=50, label='Points du Chemin', transform=ccrs.PlateCarree())

        # Enregistrer le plot si l'option `save_plots` est activée
        if save_plots:
            os.makedirs(output_dir, exist_ok=True)  # Créer le répertoire si nécessaire
            plot_filename = os.path.join(output_dir, f"carte_vents_step_{step_index}.png")
            plt.savefig(plot_filename)
            print(f"Plot enregistré sous : {plot_filename}")

        plt.tight_layout()
        # Montrer les plots seulement si `save_plots` est False
        if not save_plots:
            plt.show()  # Afficher les plots
    
def get_wind_from_grib(lat, lon, time_step=0):
    """
    Récupère les composantes u10 et v10 du vent à partir du voisin le plus proche.
    """
    
    lon = lon % 360
    
    # Utiliser les valeurs de u10 et v10 préchargées
    u10_time_step = u10_values[time_step]
    v10_time_step = v10_values[time_step]
    
    latitudes = ds.latitude.values
    longitudes = ds.longitude.values
    
    # Calculer les différences de latitude et longitude
    lat_diff = np.abs(latitudes - lat)
    lon_diff = np.abs(longitudes - lon)
    
    # Calcul des distances et index du voisin le plus proche
    distances = lat_diff[:, None]**2 + lon_diff**2
    closest_index = np.unravel_index(np.argmin(distances), distances.shape)
    
    # Récupération des valeurs pour le voisin le plus proche
    u10 = u10_time_step[closest_index]
    v10 = v10_time_step[closest_index]
    
    # Calcul de la vitesse et de l'angle
    v_vent = np.sqrt((u10)**2 + v10**2) 
    a_vent = (np.degrees(np.arctan2(-u10, -v10))) % 360 
    
    return v_vent, a_vent

def enregistrement_route(chemin_x, chemin_y, pas_temporel, loc, output_dir='./', skip = 4):
    
    # Créer le répertoire de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    point = 0
    heure = 0

    for _ in range(0, len(chemin_x)):
        plt.figure(figsize=(12, 7)) 

        # Choisir les données de vent pour l'heure actuelle
        u10_specific = ds['u10'].isel(step=int(heure))
        v10_specific = ds['v10'].isel(step=int(heure))
        wind_speed = np.sqrt(u10_specific**2 + v10_specific**2)

        # Créer un sous-plot
        ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.set_extent(loc, crs=ccrs.PlateCarree())

        # Ajouter des features de la carte
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAND, facecolor='lightgray')
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

        # Tracer la route idéale jusqu'à l'heure actuelle
        ax.plot(chemin_x[:point + 1], chemin_y[:point + 1], color='black', linestyle='-', linewidth=2, label='Chemin Idéal', transform=ccrs.PlateCarree())
        ax.scatter(chemin_x[:point + 1], chemin_y[:point + 1], color='black', s=50, transform=ccrs.PlateCarree())

        point += 1
        
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

        plt.close() 
        heure += pas_temporel
        
def point_ini_fin(loc):
    points = []

    def on_click(event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            points.append((x, y))
            print(f"Point sélectionné: x={x}, y={y}")

            # On ajoute les points une fois cliqué
            ax.scatter(x, y, color='red', s=100, zorder=5, transform=ccrs.PlateCarree())
            plt.draw()  

            # Pas plus de deux points
            if len(points) == 2:
                fig.canvas.mpl_disconnect(cid)  

    fig, ax = plt.subplots(figsize=(12, 7), subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Localisation de la carte
    ax.set_extent(loc, crs=ccrs.PlateCarree())
    
    # Paramètre de résolution
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=1)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linestyle=':')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    
    # Tracer une grille de latitude/longitude
    gl = ax.gridlines(draw_labels=True, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False

    # Connecter l'événement de clic
    cid = fig.canvas.mpl_connect('button_press_event', on_click)
    
    plt.title("Cliquez pour choisir le point de départ et le point final")
    plt.show()
    
    if len(points) == 2:
        return points[0], points[1]
    else:
        print("Sélection incomplète.")
        return None

def is_on_land(segment):
    """
    Vérifie si un segment coupe la terre, en excluant les polygones trop éloignés.

    Args:
    - segment (LineString): Segment représenté sous forme de LineString.
    - land_polygons_sindex: Index spatial des polygones de terre.
    - land_polygons: Polygones de terre.
    - distance_threshold (float): Seuil de distance en kilomètres pour éviter les polygones lointains.

    Returns:
    - bool: True si le segment coupe la terre, False sinon.
    """
    # Calculer les points les plus proches pour le filtrage
    start, end = segment.coords[0], segment.coords[1]
    segment_midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)

    possible_matches_index = list(land_polygons_sindex.intersection(segment.bounds))
    possible_matches = land_polygons.iloc[possible_matches_index]

    for polygon in possible_matches.geometry:
        # Vérification rapide de distance
        nearest = nearest_points(segment, polygon)
        if geodesic((nearest[0].y, nearest[0].x), (nearest[1].y, nearest[1].x)).km > 10:
            continue  # Passer aux autres polygones si trop éloigné

        # Vérification de l'intersection précise si proche
        if segment.intersects(polygon):
            return True

    return False
  
#Chemin d'accès du fichier GRIB vent et courant (pas encore fait)
file_path = 'C:/Users/arthu/OneDrive/Arthur/Programmation/TIPE_Arthur_Lhoste/Logiciel/Données_vent/METEOCONSULT12Z_VENT_1105_Gascogne.grb'
file_path_courant = 'C:/Users/arthu/OneDrive/Arthur/Programmation/TIPE_Arthur_Lhoste/Logiciel/Données_vent/METEOCONSULT00Z_COURANT_0921_Gascogne.grb'

# On charge les datasets
ds = xr.open_dataset(file_path, engine='cfgrib')
ds_ = xr.open_dataset(file_path_courant, engine = 'cfgrib')

# On charges les composantes u10 et v10 du vent au début comme ça pas besoin de le recalculer à chaque fois qu'on éxecute la fonction
u10_values = [ds.u10.isel(step=int(step)).values for step in range(ds.dims['step'])]
v10_values = [ds.v10.isel(step=int(step)).values for step in range(ds.dims['step'])]

"CE QUI SUIT EST POUR LA FONCTION IS_ONLAND"

# Charger et simplifier les points centraux des polygones
land_polygons = gpd.read_file(r"C:\Users\arthu\OneDrive\Arthur\Programmation\TIPE_Arthur_Lhoste\Logiciel\Carte_frontières_terrestre\ne_50m_land.shp")
land_polygons_sindex = land_polygons.sindex

