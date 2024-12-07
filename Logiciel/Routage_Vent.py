#Je sépare la partie vent du code afin de rendre le code plus compréhensible
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import pandas as pd
import openpyxl

from time import time
import os
import Paramètres as p
from scipy.interpolate import griddata

from cartopy import crs as ccrs, feature as cfeature

from shapely.ops import nearest_points
from geopy.distance import geodesic
from shapely.geometry import LineString, Point

import geopandas as gpd
import xarray as xr

def excel_to_uv_components(excel_file):
    # Lire le fichier Excel
    data = pd.read_excel(excel_file, header=None)
    
    # Lire les paramètres initiaux
    lat_i, lon_i, grid_size = data.iloc[1, 0], data.iloc[1, 1], data.iloc[1, 2]
    nb_col, nb_lig = data.shape[1] - 1, data.shape[0] - 4
    
    # Déterminer les limites de latitude et longitude
    lat_max = lat_i - grid_size * nb_lig
    lon_max = lon_i + grid_size * nb_col

    # Construire les grilles de latitudes et longitudes
    latitudes = np.linspace(lat_i, lat_max, nb_lig)
    longitudes = np.linspace(lon_i, lon_max, nb_col)

    # Extraire les données u et v
    u_values = []
    v_values = []
    for i in range(nb_lig):
        u_row = []
        v_row = []
        for j in range(nb_col):
            u_v = data.iloc[4 + nb_lig - 1 - i, j + 1].split(';')
            u_row.append(float(u_v[0]))  # Composante u
            v_row.append(float(u_v[1]))  # Composante v
        u_values.append(u_row)
        v_values.append(v_row)

    # Convertir en numpy arrays
    u_values = np.array(u_values)
    v_values = np.array(v_values)

    # Ajouter une dimension temporelle pour simuler des données GRIB
    u = u_values[np.newaxis, :, :]  # Shape: [1, latitude, longitude]
    v = v_values[np.newaxis, :, :]  # Shape: [1, latitude, longitude]

    return u, v, latitudes, longitudes

def plot_wind_map(lon, lat, u, v, pos_i, pos_f, chemin_x=None, chemin_y=None):
        # Ajuster les données si vent_start_line est spécifié

    lat = lat[5:]
    u = u[:, 5:, :]
    v = v[:, 5:, :]

    # Si lon et lat sont 1D, créez une grille 2D
    if lon.ndim == 1 and lat.ndim == 1:
        lon, lat = np.meshgrid(lon, lat)
    
    # Suppression des dimensions inutiles
    u = u.squeeze()
    v = v.squeeze()
    
    # Vérification des dimensions
    if lon.shape != lat.shape or u.shape != v.shape or lon.shape != u.shape:
        raise ValueError("Les dimensions de lon, lat, u et v doivent correspondre.")
    
    # Calcul de la magnitude du vent
    wind_magnitude = np.sqrt(u**2 + v**2)
    
    # Création d'une grille régulière pour interpolation
    lon_lin = np.linspace(lon.min(), lon.max(), 300)
    lat_lin = np.linspace(lat.min(), lat.max(), 300)
    lon_interp, lat_interp = np.meshgrid(lon_lin, lat_lin)
    
    # Interpolation des données sur la nouvelle grille
    u_interp = griddata((lon.ravel(), lat.ravel()), u.ravel(), (lon_interp, lat_interp), method='cubic')
    v_interp = griddata((lon.ravel(), lat.ravel()), v.ravel(), (lon_interp, lat_interp), method='cubic')
    
    # Vérification post-interpolation
    if np.isnan(u_interp).any() or np.isnan(v_interp).any():
        raise ValueError("L'interpolation a généré des NaN.")
    
    # Affichage des données
    plt.figure(figsize=(10, 8))
    plt.contourf(lon_interp, lat_interp, np.sqrt(u_interp**2 + v_interp**2), cmap='viridis', levels=100)
    plt.quiver(lon, lat, -u, -v, color='black', angles='xy', scale_units='xy', scale=50)
    plt.scatter(pos_i[0], pos_i[1], color='green', s=100, label='Position Initiale')
    plt.scatter(pos_f[0], pos_f[1], color='red', s=100, label='Position Finale')
    if chemin_x is not None and chemin_y is not None:
        plt.plot(chemin_x, chemin_y, color='black', linestyle='-', linewidth=2, label='Chemin Idéal')
    plt.colorbar(label='Magnitude du vent')
    plt.legend()
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Carte des Vents avec Chemin Idéal et Interpolation')
    plt.grid(True)
    plt.show()
     
def plot_wind(loc, step_indices=[1], chemin_x=None, chemin_y=None, skip=1, save_plots=False, output_dir= p.output_dir):
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

def plot_wind2(ax, loc, step_indices=[1], chemin_x=None, chemin_y=None):
    ax.set_extent(loc, crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('10m'), linewidth=1)
    ax.add_feature(cfeature.BORDERS.with_scale('10m'), linestyle=':')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    ax.scatter(p.position_finale[0], p.position_finale[1], color='black', s=100, marker='*', label='Position Finale')

    # Définir une colormap personnalisée pour les plages de vent
    colors = [
        (0/60, "#6271B7"),
        (2/60, "#39619F"),
        (6/60, "#4A94A9"),
        (10/60, "#4D8D7B"),
        (14/60, "#53A553"),
        (17/60, "#359F35"),
        (21/60, "#A79D51"),
        (25/60, "#9F7F3A"),
        (29/60, "#9F7F3A"),
        (33/60, "#A16C5C"),
        (37/60, "#813A4E"),
        (41/60, "#AF5088"),
        (44/60, "#754A93"),
        (47/60, "#6D61A3"),
        (52/60, "#44698D"),
        (56/60, "#5C9098"),
        (60/60, "#5C9098")
    ]
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_wind", colors)
    norm = mcolors.Normalize(vmin=0, vmax=60)

    for step_index in step_indices:
        if p.type == "grib":
            try:
                # GRIB : Extraire les données pour l'étape spécifiée
                u10_specific = ds['u10'].isel(step=int(step_index))
                v10_specific = ds['v10'].isel(step=int(step_index))
                latitudes = ds['latitude'].values
                longitudes = ds['longitude'].values
            except Exception as e:
                u10_specific = ds['u10'].isel(step=int(-1))
                v10_specific = ds['v10'].isel(step=int(-1))
                latitudes = ds['latitude'].values
                longitudes = ds['longitude'].values

        elif p.type == "excel":
            # Excel : Les données ne changent pas selon l'étape (pas de temps)
            u10_specific = u_xl[0]
            v10_specific = v_xl[0]
            latitudes = lat_xl
            longitudes = lon_xl

        else:
            raise ValueError("La source spécifiée doit être 'grib' ou 'excel'.")

        latitudes = latitudes[::p.skip]
        longitudes = longitudes[::p.skip]
        u10_specific = u10_specific[::p.skip, ::p.skip]
        v10_specific = v10_specific[::p.skip, ::p.skip]

        # Calcul de la vitesse du vent
        wind_speed = np.sqrt(u10_specific**2 + v10_specific**2)

        # Colorier la carte avec les vitesses du vent
        mesh = ax.pcolormesh(
            longitudes, latitudes, wind_speed,
            transform=ccrs.PlateCarree(),
            cmap=cmap, norm=norm, shading='auto'
        )

        # Ajouter des vecteurs noirs pour la direction
        q = ax.quiver(
            longitudes[::2*p.skip], latitudes[::2*p.skip],
            u10_specific[::2*p.skip, ::2*p.skip], v10_specific[::2*p.skip, ::2*p.skip],
            color='black', scale=1000, transform=ccrs.PlateCarree()
        )

        # Ajouter une barre de couleur pour l'intensité
        if p.drapeau:
            cbar = plt.colorbar(
                mappable=mesh, ax=ax, orientation='vertical', pad=0.02, shrink=0.5
            )
            cbar.set_label("Vitesse du vent (nœuds)")
        p.drapeau = False

        # Tracer le chemin idéal s'il est fourni
        if chemin_x is not None and chemin_y is not None:
            ax.plot(chemin_x, chemin_y, color='black', linestyle='-', linewidth=2, label='Chemin Idéal', transform=ccrs.PlateCarree())
            ax.scatter(chemin_x, chemin_y, color='black', s=50, transform=ccrs.PlateCarree())

def get_wind_at_position(lat, lon, time_step=0):
    try:
            
        lon = lon % 360  # Assurez-vous que la longitude est dans la plage [0, 360]

        if p.type == 'grib':
            # Sélection des données temporelles
            u_time_step = u10_values[time_step]
            v_time_step = v10_values[time_step]
            latitudes = ds.latitude.values
            longitudes = ds.longitude.values

        elif p.type == 'excel':
            u_time_step = u_xl[0]
            v_time_step = v_xl[0]
            latitudes = lat_xl
            longitudes = lon_xl

        else:
            raise ValueError("La source spécifiée doit être 'grib' ou 'excel'.")

        # Calcul des distances
        lat_diff = np.abs(latitudes - lat)
        lon_diff = np.abs(longitudes - lon)

        if lat_diff.ndim == 1 and lon_diff.ndim == 1:  # Coordonnées 1D
            distances = lat_diff[:, None]**2 + lon_diff**2
        else:  # Coordonnées 2D
            distances = lat_diff**2 + lon_diff**2

        # Trouver l'index du point le plus proche
        closest_index = np.unravel_index(np.argmin(distances), distances.shape)

        # Récupérer les valeurs de vent
        u = u_time_step[closest_index]
        v = v_time_step[closest_index]

        # Calcul de la vitesse et de l'angle
        v_vent = np.sqrt(u**2 + v**2)
        a_vent = (np.degrees(np.arctan2(-u, -v))) % 360

        return v_vent, a_vent
        
    except Exception as e:
        return get_wind_at_position(lat, lon, -1)

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

def is_on_land(parent, point, distance_threshold=10):

    # Construire un segment entre le point parent et l'enfant
    segment = LineString([parent, point])
    
    # Obtenir les indices des polygones potentiellement concernés
    possible_matches_index = list(land_polygons_sindex.intersection(segment.bounds))
    possible_matches = land_polygons.iloc[possible_matches_index]
    
    # Vérifier directement si le parent ou l'enfant est sur la terre
    for polygon in possible_matches.geometry:
        if polygon.contains(Point(parent)) or polygon.contains(Point(point)):
            return True

    # Vérifier l'intersection ou la proximité avec les polygones
    for polygon in possible_matches.geometry:
        # Vérification rapide de distance
        nearest = nearest_points(segment, polygon)
        distance = geodesic((nearest[0].y, nearest[0].x), (nearest[1].y, nearest[1].x)).km
        if distance > distance_threshold:
            continue  # Trop loin, on passe au prochain polygone
        
        # Vérification précise d'intersection
        if segment.intersects(polygon):
            return True
    
    return False

  
#Chemin d'accès du fichier GRIB vent et courant (pas encore fait)
file_path = p.vent

if p.type == 'grib':
    # On charge les datasets
    ds = xr.open_dataset(file_path, engine='cfgrib')
    # On charges les composantes u10 et v10 du vent au début comme ça pas besoin de le recalculer à chaque fois qu'on éxecute la fonction
    u10_values = [ds.u10.isel(step=int(step)).values for step in range(ds.dims['step'])]
    v10_values = [ds.v10.isel(step=int(step)).values for step in range(ds.dims['step'])]
    
else:
    u_xl, v_xl, lat_xl, lon_xl = excel_to_uv_components(p.excel_wind)
    print("Dimensions de lon_grid :", lon_xl.shape)
    print("Dimensions de lat_grid :", lat_xl.shape)
    print("Dimensions de u :", u_xl.shape)
    print("Dimensions de v :", v_xl.shape)

    # plot_wind_map(lon_xl, lat_xl, u_xl, v_xl,(-3, 47), (-7.6, 45.))


"CE QUI SUIT EST POUR LA FONCTION IS_ONLAND"

# Charger et simplifier les points centraux des polygones
land_polygons = gpd.read_file(p.land)
land_polygons_sindex = land_polygons.sindex

