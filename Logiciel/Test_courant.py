import xarray as xr
import matplotlib.pyplot as plt
import numpy as np


file_path_courant = 'C:/Users/arthu/OneDrive/Arthur/Programmation/TIPE_Arthur_Lhoste/Logiciel/Données_vent/METEOCONSULT00Z_COURANT_0921_Gascogne.grb'
ds = xr.open_dataset(file_path_courant, engine='cfgrib')

time_step = 0

# Masque pour les valeurs non nan à l'étape choisie
mask = ~np.isnan(ds['unknown'].values[time_step])

# Récupérer les valeurs de longitude et latitude
longitudes = ds['longitude'].values
latitudes = ds['latitude'].values

# Créer un meshgrid pour les coordonnées
lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)

# Tracer les données
plt.figure(figsize=(10, 6))
plt.scatter(lon_grid[mask], lat_grid[mask], 
            c=ds['unknown'].values[time_step][mask], cmap='coolwarm')
plt.colorbar(label='Valeur du Courant')
plt.title('Distribution des Courants (sans terre)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()

ds.close()
