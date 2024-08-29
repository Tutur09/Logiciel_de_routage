import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cfgrib 
import xarray as xr

# Chemin vers le fichier GRIB contenant les données de vent
fichier_grib = 'C:/Users/arthu/OneDrive/Arthur/Programmation/TIPE/grib_test.grb'

grib_data = cfgrib.open_datasets(fichier_grib)

dataset_principal = grib_data[0]

u_wind = dataset_principal['u10']
v_wind = dataset_principal['v10']

# Accéder aux variables de vent
u_wind = dataset_principal['u10']
v_wind = dataset_principal['v10']

# Créer une carte
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

print(u_wind.values)

# # Tracer les données de vent
# magnitude_wind = (u_wind.values**2 + v_wind.values**2)**0.5
# wind_plot = ax.contourf(u_wind.longitude, u_wind.latitude, magnitude_wind,
#                         transform=ccrs.PlateCarree(), cmap='coolwarm')

# # Ajouter une barre de couleur
# cbar = plt.colorbar(wind_plot, ax=ax, orientation='vertical', shrink=0.7)
# cbar.set_label('Vitesse du vent (m/s)')

# # Afficher la carte
# plt.title('Vitesse du vent')
# plt.show()