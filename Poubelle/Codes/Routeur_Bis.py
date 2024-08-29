import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from geopy.distance import geodesic
import alphashape
from shapely.geometry import Polygon, Point, LineString, MultiPolygon

# Charger les données
polaire_vitesse = pd.read_csv('C:/Users/arthu/OneDrive/Arthur/Programmation/TIPE/Sunfast3600.pol', delimiter='\t', index_col=0)
polaire_vitesse.columns = polaire_vitesse.columns.astype(float)
polaire_vitesse.index = polaire_vitesse.index.astype(float)

# Compléter les données pour les angles de 181 à 360 degrés
for angle in range(180, 0, -1):
    mirror_angle = 360 - angle
    if angle in polaire_vitesse.index:
        polaire_vitesse.loc[mirror_angle] = polaire_vitesse.loc[angle]

# Paramètres
start_lat, start_lon = 47.4833, -3.0167
wind_speed = 10.0

# Créer la figure et l'axe avec projection cartographique
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')

# Fonction pour calculer la nouvelle position basée sur la vitesse et l'angle
def calculate_new_position(lat, lon, angle, speed):
    distance_nm = speed * 0.10  # Distance parcourue en 15 minutes
    return geodesic(nautical=distance_nm).destination((lat, lon), angle)

# Simulation de la trajectoire
iterations = 4  # Nombre de répétitions du calcul pour chaque nouveau point
tolerance = 0.001  # Pour la précision des points sur l'enveloppe concave
alpha = 100  # Paramètre alpha pour contrôler la concavité

points_to_analyse = [(start_lat, start_lon)]  # Initialisation : on place le bateau à une coordonnée choisie

all_points = []  # Stocke l'ensemble des points

for _ in range(iterations):
    new_points = []
    for point in points_to_analyse:
        current_lat, current_lon = point
        for angle in np.arange(0, 361, 30):
            if angle in polaire_vitesse.index and wind_speed in polaire_vitesse.columns:
                boat_speed = polaire_vitesse.at[angle, wind_speed]
                new_position = calculate_new_position(current_lat, current_lon, angle, boat_speed)
                new_points.append((new_position.latitude, new_position.longitude))
                all_points.append((new_position.latitude, new_position.longitude))
                ax.scatter(new_position.longitude, new_position.latitude, color='blue', transform=ccrs.PlateCarree())

    # Construction de l'enveloppe concave avec tous les points générés
    swapped_points = [(lon, lat) for lat, lon in all_points]
    concave_hull = alphashape.alphashape(swapped_points, alpha)

    # Extraire les points du contour de l'enveloppe concave pour la prochaine itération
    points_on_hull = []
    if isinstance(concave_hull, (Polygon, MultiPolygon)):
        for geom in concave_hull.geoms if isinstance(concave_hull, MultiPolygon) else [concave_hull]:
            x, y = geom.exterior.xy
            ax.plot(x, y, 'r-', transform=ccrs.PlateCarree(), label='Concave Hull' if _ == 0 else "")
            for i in range(len(x)):
                points_on_hull.append((y[i], x[i]))  # Notez que les coordonnées sont inversées ici pour correspondre à lat, lon
    elif isinstance(concave_hull, (Point, LineString)):
        x, y = concave_hull.xy
        ax.plot(x, y, 'g-', label='Single Point or Line' if _ == 0 else "")
        points_on_hull = list(zip(y, x))  # Pour un seul point ou une ligne, traiter de la même manière

    # Actualiser les points à analyser pour la prochaine itération avec les points de l'enveloppe concave
    points_to_analyse = points_on_hull

# Assurer que la légende est ajoutée une seule fois
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys())

plt.show()
