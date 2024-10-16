import matplotlib.pyplot as plt
import mplleaflet

# Coordonnées des points marins (latitude, longitude)
latitudes = [48.8566, 43.6045]  # Paris, Toulouse
longitudes = [2.3522, 1.4440]

# Création d'une figure
plt.figure(figsize=(8, 6))

# Tracer les points
plt.scatter(longitudes, latitudes, marker='o', color='blue', s=100)

# Ajout des titres
plt.title('Carte Marine Simple')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# Conversion en carte interactive
mplleaflet.show()
