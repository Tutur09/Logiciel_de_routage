import numpy as np
import pandas as pd
import math
import time

import matplotlib.pyplot as plt
from matplotlib.path import Path

import alphashape
from shapely.geometry import Point, MultiPoint, LineString, MultiPolygon, Polygon, MultiLineString
from scipy.spatial import Delaunay
from cartopy import crs as ccrs, feature as cfeature

import Routage_Vent_en_dev as rv
from scipy.spatial import cKDTree



def projection(position, cap, distance):
    long_ini = position[0]
    lat_ini = position[1]
    
    # Earth radius in nautical miles
    R = 3440.0
    
    # Convert latitude and longitude from degrees to radians
    lat_ini_rad = math.radians(lat_ini)
    long_ini_rad = math.radians(long_ini)
    
    # Convert bearing to radians
    bearing_rad = math.radians(cap)
    
    # Distance ratio compared to the earth's radius
    distance_ratio = distance / R
    
    # Calculate new latitude in radians
    new_lat_rad = math.asin(math.sin(lat_ini_rad) * math.cos(distance_ratio) + 
                            math.cos(lat_ini_rad) * math.sin(distance_ratio) * math.cos(bearing_rad))
    
    # Calculate new longitude in radians
    new_long_rad = long_ini_rad + math.atan2(math.sin(bearing_rad) * math.sin(distance_ratio) * math.cos(lat_ini_rad),
                                             math.cos(distance_ratio) - math.sin(lat_ini_rad) * math.sin(new_lat_rad))
    
    # Convert new latitude and longitude to degrees
    new_lat = math.degrees(new_lat_rad)
    new_long = math.degrees(new_long_rad)
    
    return (new_long, new_lat)

def prochains_points(position, pol_v_vent, d_vent, pas_temporel, pas_angle):
    liste_points = []
    start =time.time()

    chemin = list(range(0, 360, pas_angle))
    for angle in chemin:
        v_bateau = 1.5 * recup_vitesse_fast(pol_v_vent, d_vent - angle)
        liste_points.append(projection(position, angle, v_bateau * pas_temporel))
    stop = time.time()
    #print(stop - start)
    return liste_points

def prochains_points_liste_parent_enfants(liste, pas_temporel, pas_angle, filtrer_par_distance=False, point_arrivee=None, heure=0, land_polygons_sindex=None, land_polygons=None, tolerance=0.01):
    """
    Génère des sous-listes de parents et d'enfants pour chaque point parent avec une zone de tolérance autour du point d'arrivée.

    Args:
        liste (list): Liste des positions parents.
        pas_temporel (float ou integer): Intervalle de temps entre les itérations.
        pas_angle (int): Incrément d'angle pour la génération des points.
        filtrer_par_distance (bool): Activer le filtrage basé sur la distance si True.
        point_arrivee (tuple): La position finale (longitude, latitude).
        heure (int): Heure pour récupérer les données de vent.
        land_polygons_sindex: Index spatial des polygones de terre.
        land_polygons: Polygones de terre.
        tolerance (float): Rayon de tolérance autour du point d'arrivée.

    Returns:
        list: Liste avec des sous-listes parents/enfants.
    """
    liste_rendu = []
    temps, temps2, temps3 = 0, 0, 0

    target_geom = Point(point_arrivee)
    target_zone = target_geom.buffer(tolerance)  # Créer la zone de tolérance

    for lon, lat in liste:
        start1 = time.time()
        v_vent, d_vent = rv.get_wind_from_grib(lat, lon, heure)
        stop1 = time.time()
        temps += (stop1 - start1)

        start2 = time.time()
        pol_v_vent = polaire(v_vent)
        stop2 = time.time()
        temps2 += stop2 - start2

        enfants = prochains_points((lon, lat), pol_v_vent, d_vent, pas_temporel, pas_angle)
        parent_point = (lon, lat)

        start3 = time.time()
        adjusted_enfants = []
        for enfant in enfants:
            #segment = LineString([parent_point, enfant])
            
            # Vérification de la distance
            if filtrer_par_distance and point_arrivee is not None:
                if plus_proche_que_parent(point_arrivee, parent_point, enfant):
                    # Vérification de l'intersection uniquement si les conditions précédentes sont vraies
                    # if segment.intersects(target_zone):
                    #     projected_point = segment.interpolate(segment.project(target_geom))
                    #     adjusted_enfants.append((projected_point.x, projected_point.y))
                    #     break
                    adjusted_enfants.append(enfant)
                    
        stop3 = time.time()
        temps3 += stop3 - start3
        # if not adjusted_enfants:  # Ensure there's at least one child
        #     adjusted_enfants = [parent_point]  # Add the parent as a fallback to avoid empty lists
        

        liste_rendu.append([parent_point, adjusted_enfants])

    print("temps get_wind ", temps)
    print("temps polaire", temps2)
    print("temps vérif", temps3)

    return liste_rendu

def plus_proche_que_parent(point_arrivee, pos_parent, pos_enfant):
    distance_parent = math.sqrt((point_arrivee[0] - pos_parent[0])**2 + (point_arrivee[1] - pos_parent[1])**2)
    distance_enfant = math.sqrt((point_arrivee[0] - pos_enfant[0])**2 + (point_arrivee[1] - pos_enfant[1])**2)
    return distance_enfant < distance_parent

def polaire(vitesse_vent):
    liste_vitesse = polaire_df.columns

    i = 0
    while i < len(liste_vitesse):
        vitesse = float(liste_vitesse[i])
        if vitesse == vitesse_vent:
            return polaire_df[liste_vitesse[i]]
        elif vitesse > vitesse_vent:
            inf = i - 1
            sup = i
            t = (vitesse_vent - float(liste_vitesse[inf])) / (float(liste_vitesse[sup]) - float(liste_vitesse[inf]))
            return t * polaire_df[liste_vitesse[inf]] + (1 - t) * polaire_df[liste_vitesse[sup]]
        i += 1
    print('Erreur vitesse de vent')
    return None

def recup_vitesse_fast(pol_v_vent, angle):
    if pol_v_vent is None:
        raise ValueError("Erreur : pol_v_vent est None, vérifiez la vitesse du vent.")
    
    angle = abs(angle)
    if angle > 180:
        angle = 360 - angle

    liste_angle = pol_v_vent.index

    i = 0
    while i < len(pol_v_vent):
        angle_vent = float(liste_angle[i])
        if angle == angle_vent:
            return pol_v_vent[liste_angle[i]]
        elif angle_vent > angle:
            inf = i - 1
            sup = i
            t = (angle - float(liste_angle[inf])) / (float(liste_angle[sup]) - float(liste_angle[inf]))
            return t * pol_v_vent[liste_angle[inf]] + (1 - t) * pol_v_vent[liste_angle[sup]]
        i += 1
    print('Erreur angle')
    return None

def filtrer_points_proches(liste_points, seuil_distance=0.001):
    """
    Filtre les points trop proches les uns des autres pour réduire le nombre de points d'entrée.

    Args:
        liste_points (list): Liste des points (x, y) à filtrer.
        seuil_distance (float): Distance minimale entre les points conservés.

    Returns:
        list: Liste des points filtrés.
    """
    points = np.array(liste_points)
    
    # Ensure `points` has the shape (n, m) before passing to cKDTree
    if points.ndim == 1:
        points = points.reshape(-1, 2)  # Assuming 2D points; adjust dimensions if needed
    
    arbre = cKDTree(points)    
    indices_a_conserver = []

    # Marquer les points déjà conservés pour éviter les doublons
    deja_conserves = np.full(points.shape[0], False)

    for i in range(points.shape[0]):
        if not deja_conserves[i]:
            # Trouver tous les points dans le seuil de distance et les marquer comme conservés
            voisins = arbre.query_ball_point(points[i], r=seuil_distance)
            indices_a_conserver.append(i)
            deja_conserves[voisins] = True

    return points[indices_a_conserver].tolist()

import numpy as np
import alphashape
from shapely.geometry import MultiPoint

def forme_concave(liste_points, alpha):
    """
    Génère une enveloppe concave des points avec le paramètre alpha.

    Args:
        liste_points (list): Liste de tuples (x, y).
        alpha (float): Paramètre alpha pour contrôler la "concavité" de la forme.

    Returns:
        list: Liste des points qui forment le contour de l'enveloppe concave, ou une liste vide si aucune enveloppe n'est générée.
    """
    # Supprimer les doublons dans les points
    points = np.unique(np.array(liste_points), axis=0)

    # Générer l'enveloppe concave
    alpha_shape = alphashape.alphashape(points, alpha)

    # Vérifier si l'enveloppe est vide
    if alpha_shape.is_empty:
        print("Avertissement : l'enveloppe concave est vide.")
        return []

    # Extraire les points de l'enveloppe concave
    if hasattr(alpha_shape, "exterior"):
        return list(alpha_shape.exterior.coords)
    else:
        return []



def flatten_list(nested_list):
    flattened_list = []
    
    def _flatten(element):
        if isinstance(element, list):
            for item in element:
                _flatten(item)
        else:
            flattened_list.append(element)
    
    _flatten(nested_list)
    return flattened_list

def is_point_in_hull(point, hull):
    hull_path = np.array(hull)
    path = Path(hull_path)
    return path.contains_point(point)

def distance(point1, point2):
    """
    Calcule la distance euclidienne entre deux points.
    """
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def dist_bateau_point(points, point_final, n):
    """
    Vérifie s'il existe un point dans 'points' qui est à une distance n ou moins du 'point_final'

    :param points: Liste de tuples, chaque tuple représentant un point (x, y).
    :param point_final: Tuple représentant le point final (x_final, y_final).
    :param n: Distance maximale pour la proximité.
    :return: True si un point est à une distance n ou moins, sinon False.
    """
    x_final, y_final = point_final
    
    for (x, y) in points:
        distance = math.sqrt((x - x_final) ** 2 + (y - y_final) ** 2)
        if distance <= n:
            return True
    
    return False

def plot_points(liste_parents_enfants, enveloppe_convexe, position_finale):
    couleurs = plt.get_cmap('tab20')
    for i, (parent, enfants) in enumerate(liste_parents_enfants):
        couleur = couleurs(i / len(liste_parents_enfants))
        plt.scatter(parent[0], parent[1], color=couleur, s=100, label=f'Parent {i+1}')
        for enfant in enfants:
            plt.scatter(enfant[0], enfant[1], color=couleur, s=50)
            plt.plot([parent[0], enfant[0]], [parent[1], enfant[1]], color=couleur, linestyle='-', linewidth=1)

    if len(enveloppe_convexe) > 0:
        hull_x, hull_y = zip(*enveloppe_convexe)
        plt.plot(hull_x + (hull_x[0],), hull_y + (hull_y[0],), 'r--', lw=2, label='Enveloppe Convexe')

    plt.pause(0.5)
    
def plot_point_live(ax, enveloppe_concave, couleur='blue'):
    if not enveloppe_concave:  # Vérification que l'enveloppe n'est pas vide
        return

    # Tracer la ligne fermée de l'enveloppe concave
    hull_x, hull_y = zip(*enveloppe_concave)
    ax.plot(hull_x + (hull_x[0],), hull_y + (hull_y[0],), color=couleur, linestyle='-', linewidth=1, transform=ccrs.PlateCarree())

    # Tracer les points de l'enveloppe concave
    ax.scatter(hull_x, hull_y, color='red', s=10, transform=ccrs.PlateCarree(), label='Envelope Points')

    plt.legend()
    plt.pause(0.05)  # Pause pour actualiser l'affichage en live

def itere_jusqua_dans_enveloppe(position_initiale, position_finale, pas_temporel, pas_angle, tolerance, loc, live=False, enregistrement=True):
    heure = 13
    start_i = time.time()
    temp = pas_temporel
    positions = [position_initiale]
    iter_count = 0
    parent_map = {position_initiale: None}
    target_geom = Point(position_finale)
    target_zone = target_geom.buffer(tolerance)  # Zone de tolérance autour du point final

    if live:
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent(loc, crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=1)
        ax.add_feature(cfeature.BORDERS.with_scale('50m'), linestyle=':')
        ax.add_feature(cfeature.LAND, facecolor='lightgray')
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
        ax.scatter(position_finale[0], position_finale[1], color='black', s=100, marker='*', label='Position Finale')
        plt.title('Itération et Enveloppe Concave')
        plt.grid(True)
        plt.legend()

    
    while True:
        print(f"Iteration {iter_count}:")
        print('Heure ', heure)

        start = time.time()
        liste_parents_enfants = prochains_points_liste_parent_enfants(positions, temp, pas_angle, True, position_finale, heure=heure)
        stop = time.time()

        heure += pas_temporel
        print("temps liste_parents_enfants ", stop - start)

        points_aplatis = flatten_list(liste_parents_enfants)
        #points_reduits = filtrer_points_proches(points_aplatis, seuil_distance=0.001)
        #print("Nombre de points dans points_reduits:", len(points_reduits))


        t1= time.time()
        enveloppe_concave = forme_concave(points_aplatis, 3)
        print("Nombre de points dans enveloppe_concave:", len(enveloppe_concave))

        s1 = time.time()
        print("temps envconc ", s1 - t1)
        if live:
            plot_point_live(ax, enveloppe_concave)
                
        for parent, enfants in liste_parents_enfants:
            for enfant in enfants:
                if enfant not in parent_map:
                    parent_map[enfant] = parent

        # Mettre à jour les positions pour la prochaine itération
        positions = enveloppe_concave
        print("le nombre de points est : ", len(positions))

        if dist_bateau_point(positions, position_finale, 0.01):
            print("validé")
            if temp >= 0.5:
                temp *= 2/3

        # Trouve le point le plus proche du point final 
        start_cp = time.time()
        if not enveloppe_concave:
            raise ValueError("Erreur : enveloppe_concave est vide alors qu'elle ne devrait pas l'être.")

        closest_point = min(enveloppe_concave, key=lambda point: distance(point, position_finale))
        stop_cp = time.time()
        print('distance arrivée, point_plus_proche ', distance(closest_point, position_finale), " temps ", start_cp - start_cp)

        # Vérifie si le point dans la zone de tolérance (déterminé par le buffer)
        if any(target_zone.contains(Point(point)) for point in positions):
            print("Un point de l'enveloppe est dans la zone de tolérance. Chemin terminé.")
            
            chemin_ideal = []
            current_point = closest_point
            while current_point is not None:
                chemin_ideal.append(current_point)
                current_point = parent_map[current_point]
            
            chemin_ideal.reverse()
            chemin_x, chemin_y = zip(*chemin_ideal)
            
            stop_f = time.time()
            print("temps_total ", stop_f-start_i)
            if not live:
                rv.plot_wind(loc, chemin_x=chemin_x, chemin_y=chemin_y)
            
            if live:
                ax.plot(chemin_x, chemin_y, color='black', linestyle='-', linewidth=2, label='Chemin Idéal')
                ax.scatter(chemin_x, chemin_y, color='black', s=50)
                plt.show()
                
            break
        
        iter_count += 1
    
    if enregistrement:
        lien_dossier = r"C:\Users\arthu\OneDrive\Arthur\Programmation\TIPE_Arthur_Lhoste\route_ideale"
        rv.enregistrement_route(chemin_x, chemin_y, pas_temporel, loc, output_dir=lien_dossier)
    
    return liste_parents_enfants




#Avant dans la fonction polaire, mais je le sors pour le calculer une fois
polaire_df = pd.read_csv('Sunfast3600.pol', delimiter=r'\s+', index_col=0)