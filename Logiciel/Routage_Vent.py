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
import pickle

def excel_to_uv_components2(excel_file):
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

def excel_to_uv_components(excel_file):
    # Lecture du fichier Excel, en considérant la première ligne comme en-têtes de colonnes
    # et la première colonne (lat\lon, 65, 64, etc.) comme index.
    df = pd.read_excel(excel_file, header=0, index_col=0)
    
    # À présent, df.index contient les latitudes et df.columns contient les longitudes.
    # Convertir ces valeurs en type float (elles devraient déjà être numériques, sinon forcées)
    latitudes = df.index.astype(float).values
    longitudes = df.columns.astype(float).values

    # Chaque cellule contient une chaîne du type "U;V"
    # On va les convertir en tuples (u, v).
    def parse_uv(cell):
        # Séparer sur le point-virgule
        u_str, v_str = cell.split(';')
        # Remplacer la virgule par un point si nécessaire et convertir en float
        u_val = float(u_str.replace(',', '.'))
        v_val = float(v_str.replace(',', '.'))
        return (u_val, v_val)

    # Appliquer ce parsing à chaque cellule
    uv_values = df.applymap(parse_uv)

    # Extraire les composantes u et v dans deux tableaux distincts
    u_values = uv_values.applymap(lambda x: x[0]).values
    v_values = uv_values.applymap(lambda x: x[1]).values

    # Ajouter une dimension temporelle (simule un pas de temps unique) pour rester cohérent avec le format "GRIB"
    u = u_values[np.newaxis, :, :]  # Shape: (1, nombre_de_latitudes, nombre_de_longitudes)
    v = v_values[np.newaxis, :, :]

    return u, v, latitudes, longitudes

def plot_wind2(ax, loc, step_indices=[1], chemin_x=None, chemin_y=None):
    ax.set_extent(loc, crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('10m'), linewidth=1)
    ax.add_feature(cfeature.BORDERS.with_scale('10m'), linestyle=':')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    ax.scatter(p.position_finale[0], p.position_finale[1], color='black', s=100, marker='*', label='Position Finale')

    # Définir les plages de vitesse du vent et les couleurs associées
    cmap = mcolors.ListedColormap(p.colors_windy)
    norm = mcolors.BoundaryNorm(p.wind_speed_bins, cmap.N)

    for step_index in step_indices:
        if p.type == "grib":
            try:
                # GRIB : Extraire les données pour l'étape spécifiée
                u10_specific = ds['u10'].isel(step=int(step_index)).values
                v10_specific = ds['v10'].isel(step=int(step_index)).values
                latitudes = ds['latitude'].values
                longitudes = ds['longitude'].values
            except Exception as e:
                u10_specific = ds['u10'].isel(step=int(-1)).values
                v10_specific = ds['v10'].isel(step=int(-1)).values
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

        # Sous-échantillonnage
        latitudes = latitudes[::p.skip]
        longitudes = longitudes[::p.skip]
        u10_specific = u10_specific[::p.skip, ::p.skip]
        v10_specific = v10_specific[::p.skip, ::p.skip]

        # Calcul de la vitesse du vent
        wind_speed = 1.852 * np.sqrt(u10_specific**2 + v10_specific**2)

        # Colorier la carte avec les vitesses du vent
        mesh = ax.pcolormesh(
            longitudes, latitudes, wind_speed,
            transform=ccrs.PlateCarree(), cmap=cmap, norm=norm, shading='auto'
        )

        # Ajouter des vecteurs noirs pour la direction
        q = ax.quiver(
            longitudes[::p.skip], latitudes[::p.skip],
            u10_specific[::p.skip, ::p.skip], v10_specific[::p.skip, ::p.skip],
            color='black', scale=500, transform=ccrs.PlateCarree()
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

def plot_grib(heure, position=None, route=None, context=None):
    fig, ax = plt.subplots(figsize=(20, 16), subplot_kw={'projection': ccrs.PlateCarree()})

    manager = plt.get_current_fig_manager()
    try:
        manager.window.wm_geometry("+100+100")
    except AttributeError:
        manager.window.setGeometry(100, 100, 800, 600)


    # Mise en place de la carte
    ax.set_extent(p.loc_nav, crs=ccrs.PlateCarree())
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS.with_scale('10m'), linestyle=':')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.grid(True)

    # Définir les plages de vitesse de vent et les couleurs associées
    cmap = mcolors.ListedColormap(p.colors_windy)
    norm = mcolors.BoundaryNorm(p.wind_speed_bins, cmap.N)

    # Affichage des données de vent
    if p.type == "grib":
        try:
            # GRIB : Extraire les données pour l'étape spécifiée
            u10_specific = ds['u10'].isel(step=int(heure)).values
            v10_specific = ds['v10'].isel(step=int(heure)).values
            latitudes = ds['latitude'].values
            longitudes = ds['longitude'].values
        except Exception as e:
            u10_specific = ds['u10'].isel(step=int(-1)).values
            v10_specific = ds['v10'].isel(step=int(-1)).values
            latitudes = ds['latitude'].values
            longitudes = ds['longitude'].values
    elif p.type == "excel":
        u10_specific = u_xl[0]
        v10_specific = v_xl[0]
        latitudes = lat_xl
        longitudes = lon_xl
    else:
        raise ValueError("Source de données invalide.")

    skip = 1
    wind_speed = 1.852 * np.sqrt(u10_specific[::skip, ::skip]**2 + v10_specific[::skip, ::skip]**2)

    # Tracer la vitesse du vent
    mesh = ax.pcolormesh(
        longitudes[::skip], latitudes[::skip], wind_speed,
        transform=ccrs.PlateCarree(), cmap=cmap, norm=norm, shading='auto'
    )
    cbar = plt.colorbar(mesh, ax=ax, orientation='vertical', pad=0.02, shrink=0.5)
    cbar.set_label("Vitesse du vent (nœuds)")

    # Ajouter les vecteurs de vent
    skip_vect_vent = 6
    ax.quiver(
        longitudes[::skip_vect_vent], latitudes[::skip_vect_vent],
        u10_specific[::skip_vect_vent, ::skip_vect_vent], v10_specific[::skip_vect_vent, ::skip_vect_vent],
        scale=500, transform=ccrs.PlateCarree()
    )

    # Ajout de la route et de la position si contexte "enregistrement"
    if context == "enregistrement":
        if route:
            ax.plot(route['x'], route['y'], color='black', linestyle='-', linewidth=2, transform=ccrs.PlateCarree())
            ax.scatter(route['x'], route['y'], color='black', s=10, transform=ccrs.PlateCarree(), label='Route')

    if route:
        ax.plot(route['x'], route['y'], color='black', linestyle='-', linewidth=2, transform=ccrs.PlateCarree())
        ax.scatter(route['x'], route['y'], color='black', s=10, transform=ccrs.PlateCarree(), label='Route')
    
    if position:
        lat, lon = position
        ax.scatter(
            lon, lat, color='red', s=100, transform=ccrs.PlateCarree(), label="Position actuelle"
        )
        ax.legend(loc="upper right")

    plt.title(f"Carte des vents - Heure {heure}")

    # Afficher la figure uniquement si le contexte est None
    if context is None:
        plt.show()

    
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
        v_vent = 1.852 * np.sqrt(u**2 + v**2)
        a_vent = (np.degrees(np.arctan2(-u, -v))) % 360

        return v_vent, a_vent
        
    except Exception as e:
        return get_wind_at_position(lat, lon, -1)
    
def enregistrement_route(chemin_x, chemin_y, pas_temporel, output_dir='./', skip=4):
    # Créer le répertoire de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    point = 0
    heure = 0

    for _ in range(0, len(chemin_x)):
        # Définir la position actuelle
        position_actuelle = (chemin_y[point], chemin_x[point])

        # Appeler plot_grib avec le contexte "enregistrement"
        plot_grib(
            heure=heure,
            position=position_actuelle,
            route={
                'x': chemin_x[:point + 1],
                'y': chemin_y[:point + 1]
            },
            context="enregistrement"
        )

        # Sauvegarder la figure dans le répertoire de sortie
        plot_filename = f"{output_dir}/route_ideale_vent_heure_{heure}.png"
        plt.savefig(plot_filename)
        print(f"Plot enregistré sous : {plot_filename}")

        plt.close()
        heure += pas_temporel
        point += 1

        
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
    ds = xr.open_dataset(file_path, engine='cfgrib')
    with open("u10_values.pkl", "rb") as f:
        u10_values = pickle.load(f)
    with open("v10_values.pkl", "rb") as f:
        v10_values = pickle.load(f)
        
    # u10_values = [ds.u10.isel(step=int(step)).values for step in range(ds.dims['step'])]
    # v10_values = [ds.v10.isel(step=int(step)).values for step in range(ds.dims['step'])]

    # # Sauvegarder les variables sous forme de fichiers Pickle
    # with open("u10_values.pkl", "wb") as f:
    #     pickle.dump(u10_values, f)
    # with open("v10_values.pkl", "wb") as f:
    #     pickle.dump(v10_values, f)

else:
    u_xl, v_xl, lat_xl, lon_xl = excel_to_uv_components(p.excel_wind)
    print("Dimensions de lon_grid :", lon_xl.shape)
    print("Dimensions de lat_grid :", lat_xl.shape)
    print("Dimensions de u :", u_xl.shape)
    print("Dimensions de v :", v_xl.shape)


"CE QUI SUIT EST POUR LA FONCTION IS_ONLAND"

# Charger et simplifier les points centraux des polygones
land_polygons = gpd.read_file(p.land)
land_polygons_sindex = land_polygons.sindex
