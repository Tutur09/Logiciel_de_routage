import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from geopy.distance import geodesic
import alphashape
from shapely.geometry import Polygon, MultiPolygon

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
    distance_nm = speed * 0.25  # Distance parcourue en 15 minutes
    return geodesic(nautical=distance_nm).destination((lat, lon), angle)

# Simulation de la trajectoire
iterations = 2
points_to_analyse = [(start_lat, start_lon)]
all_points = []

for _ in range(iterations):
    new_points = []
    for point in points_to_analyse:
        current_lat, current_lon = point
        for angle in np.arange(0, 361, 10):
            if angle in polaire_vitesse.index and wind_speed in polaire_vitesse.columns:
                boat_speed = polaire_vitesse.at[angle, wind_speed]
                new_position = calculate_new_position(current_lat, current_lon, angle, boat_speed)
                new_points.append((new_position.latitude, new_position.longitude))
                all_points.append((new_position.latitude, new_position.longitude))
                ax.plot([current_lon, new_position.longitude], [current_lat, new_position.latitude], 'gx-', transform=ccrs.PlateCarree())
    points_to_analyse = new_points

# Créer l'enveloppe concave
swapped_points = [(lon, lat) for lat, lon in all_points]
alpha = 40  # Ajustez alpha pour contrôler la concavité
concave_hull = alphashape.alphashape(swapped_points, alpha)

# Tracer l'enveloppe concave et extraire les points
hull_points = []
if isinstance(concave_hull, Polygon):
    x, y = concave_hull.exterior.xy
    ax.plot(x, y, 'r-', transform=ccrs.PlateCarree(), label='Concave Hull')
    hull_points = list(concave_hull.exterior.coords)
elif isinstance(concave_hull, MultiPolygon):
    for geom in concave_hull.geoms:
        x, y = geom.exterior.xy
        ax.plot(x, y, 'g-', label='Concave Hull')
        hull_points.extend(list(geom.exterior.coords))

# Enregistrer les points de l'enveloppe concave dans un DataFrame puis dans un fichier CSV
df_hull_points = pd.DataFrame(hull_points, columns=['Longitude', 'Latitude'])
df_hull_points.to_csv('hull_points.csv', index=False)

# Imprimer les points de l'enveloppe concave
print("Points on the concave hull:")
print(df_hull_points)

# Ajouter une légende et afficher la carte
plt.legend()
plt.show()
