import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import alphashape
from shapely.geometry import Polygon

# Générer des points aléatoires
np.random.seed(0)
points_array = np.random.rand(50, 2)

# Convertir en liste de tuples
points = [tuple(point) for point in points_array]

# Calculer l'enveloppe convexe
convex_hull = ConvexHull(points_array)

# Créer l'enveloppe concave
alpha = 4  # Ajustez alpha pour contrôler la concavité
concave_hull = alphashape.alphashape(points, alpha)

# Afficher les points, l'enveloppe convexe et l'enveloppe concave
fig, ax = plt.subplots()
ax.scatter(*zip(*points), color='blue', label='Points')

# Tracer l'enveloppe convexe
for simplex in convex_hull.simplices:
    ax.plot(points_array[simplex, 0], points_array[simplex, 1], 'r-', label='Convex Hull')

# Tracer l'enveloppe concave
if isinstance(concave_hull, Polygon):
    x, y = concave_hull.exterior.xy
    ax.plot(x, y, 'g-', label='Concave Hull')
else:
    for geom in concave_hull.geoms:
        x, y = geom.exterior.xy
        ax.plot(x, y, 'g-', label='Concave Hull')

# Ajouter une légende
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys())

plt.show()

print(points)
