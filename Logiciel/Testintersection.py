from shapely.geometry import LineString, Polygon, MultiPolygon
from shapely.strtree import STRtree
import geopandas as gpd

def is_on_land_fast(parent, child, land_polygons_tree):
    """
    Vérifie rapidement si un segment entre un point parent et un enfant coupe ou touche la terre.

    Args:
        parent (tuple): Coordonnées du point parent (lon, lat).
        child (tuple): Coordonnées du point enfant (lon, lat).
        land_polygons_tree: Arbre spatial (STRtree) pour recherche rapide.

    Returns:
        bool: True si le segment touche ou coupe la terre, False sinon.
    """
    # Créer le segment
    segment = LineString([parent, child])

    # Rechercher les polygones proches avec l'arbre spatial
    possible_matches = land_polygons_tree.query(segment)

    # Vérifier les intersections avec les polygones proches
    for polygon in possible_matches:
        if not isinstance(polygon, (Polygon, MultiPolygon)):
            print(f"Objet non géométrique ignoré : {polygon}")
            continue  # Ignorer les objets non valides

        if segment.intersects(polygon):
            return True

    return False


# Charger les polygones terrestres
land_polygons = gpd.read_file(r'Logiciel\Carte_frontières_terrestre\ne_50m_land.shp')

# Filtrer uniquement les géométries valides et de type Polygon/MultiPolygon
land_polygons = land_polygons[land_polygons.geometry.is_valid & 
                              land_polygons.geometry.apply(lambda x: isinstance(x, (Polygon, MultiPolygon)))]

# Créer l'arbre spatial
land_polygons_tree = STRtree(land_polygons.geometry)


# Coordonnées du point parent et enfant
parent = (-3.635947, 47.468860)
child = (-2.482182, 47.938961) 
# Vérifier si le segment touche ou traverse la terre
result = is_on_land_fast(parent, child, land_polygons_tree)
print(result)  # True ou False
