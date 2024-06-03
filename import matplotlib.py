import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from geopy.distance import geodesic

# Charger les données depuis un fichier .pol, en ignorant les en-têtes
with open('C:/Users/arthu/OneDrive/Arthur/Programmation/TIPE/Sunfast3600.pol', 'r') as file:
    lines = file.readlines()

data = []
for line in lines[1:]:  # Sauter la première ligne (en-tête)
    # Chaque ligne contient des valeurs séparées par des espaces
    parsed_line = line.strip().split()
    data.append([float(x) for x in parsed_line])  # Convertir chaque élément en float

# Convertir la liste en DataFrame et définir la première colonne comme index (angles)
polaire_vitesse = pd.DataFrame(data)
polaire_vitesse.set_index(0, inplace=True)

# Afficher les données chargées
print(polaire_vitesse)

# Extraction des angles et des valeurs
angles_degrees = polaire_vitesse.index  # Première colonne pour les angles
angles_radians = np.radians(angles_degrees)

#plt.figure(figsize=(8, 8))
#ax = plt.subplot(111, polar=True)

# Boucler sur toutes les colonnes de valeurs après la première colonne des angles
for i in range(1, polaire_vitesse.shape[1]):
    values = polaire_vitesse.iloc[:, i].values
    values_inv = np.flip(values)
    # Préparer les angles pour la symétrie axiale autour de 180 degrés
    mirrored_angles_degrees = (360 - angles_degrees) % 360
    mirrored_angles_radians = np.flip(np.radians(mirrored_angles_degrees))

    # Concaténer les angles originaux avec les angles miroirs
    all_angles_radians = np.concatenate((angles_radians, mirrored_angles_radians))
    # Concaténer les valeurs avec elles-mêmes (inversées)
    all_values = np.concatenate((values, values_inv))

    # Tracer la courbe originale et sa symétrique
#    ax.plot(all_angles_radians, all_values, label=f'Vitesse {i} knt')

# Paramètres du graphique polaire
# ax.set_theta_zero_location('N')  # Angle zéro à Nord
# ax.set_theta_direction(-1)  # Direction des angles en sens horaire
# ax.set_title('Polaire de vitesse')
# ax.legend(loc='upper right')  # Ajouter une légende

# Afficher le graphique
#plt.show()




#Première tentative de routage : On se place avec un vent constant de 10 knt direction 0.0

pas = 0.30 #heure

# Coordonnées approximatives du milieu de la Baie de Quiberon
start_lat, start_lon = 47.4833, -3.0167

# Calculer le nouveau point à 5 NM au sud
new_point = geodesic(nautical=5).destination((start_lat, start_lon), bearing=180)  # 180 degrés pour le sud

# Créer la figure et l'axe avec projection cartographique
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': ccrs.PlateCarree()})
ax.set_extent([start_lon - 0.1, start_lon + 0.1, new_point.latitude - 0.1, start_lat + 0.1], crs=ccrs.PlateCarree())

# Ajouter les caractéristiques de la carte
ax.add_feature(cfeature.LAND)  # Correction du nom
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')

# Placer les points sur la carte
ax.plot([start_lon, new_point.longitude], [start_lat, new_point.latitude], 'bo-', markersize=5, transform=ccrs.Geodetic())
ax.text(start_lon, start_lat, 'Point de départ', horizontalalignment='right', transform=ccrs.Geodetic())
ax.text(new_point.longitude, new_point.latitude, '5 NM au sud', horizontalalignment='right', transform=ccrs.Geodetic())

# Afficher la carte
plt.show()

