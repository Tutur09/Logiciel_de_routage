import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.path import Path
import alphashape
from shapely.geometry import Point, MultiPoint
import time

import Logiciel.Routage_Vent as rv
import xarray as xr
from cartopy import crs as ccrs, feature as cfeature


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
    chemin = list(range(0, 360, pas_angle))
    for angle in chemin:
        v_bateau = recup_vitesse_fast(pol_v_vent, d_vent - angle)
        liste_points.append(projection(position, angle, v_bateau * pas_temporel))
    return liste_points

def prochains_points_liste_parent_enfants(liste, lon_grid, lat_grid, u, v, pas_temporel, pas_angle, filtrer_par_distance=False, point_arrivee=None):
    """
    Génère des sous-listes de parents et d'enfants pour chaque point parent.
    Utilise les données de vent de la carte pour calculer les trajectoires.

    Args:
        liste (list): Liste des positions parents.
        lon_grid (ndarray): Coordonnées de longitude de la grille.
        lat_grid (ndarray): Coordonnées de latitude de la grille.
        u (ndarray): Composante u des vecteurs de vent.
        v (ndarray): Composante v des vecteurs de vent.
        pas_temporel (float ou integer): Intervalle de temps entre les itérations.
        pas_angle (int): Incrément d'angle pour la génération des points.
        filtrer_par_distance (bool): Activer le filtrage basé sur la distance si True.
        point_arrivee (tuple): La position finale (longitude, latitude).

    Returns:
        list: Liste avec des sous-listes parents/enfants.
    """
    start = time.time()
    liste_rendu = []

    temps = 0
    for lon,lat in liste:
        #lon, lat = parent
        # Obtenir la direction et la force du vent pour la position actuelle      
        start1 = time.time()
        v_vent, d_vent = rv.get_wind_from_grib(lon, lat)

        stop1 = time.time()
        temps += (stop1 - start1)

        
        pol_v_vent = polaire(v_vent)


        enfants = prochains_points((lon,lat), pol_v_vent, d_vent, pas_temporel, pas_angle)
        
        

        # Filtrer les enfants selon la distance au point d'arrivée
        if filtrer_par_distance and point_arrivee is not None:
            enfants = [enfant for enfant in enfants if plus_proche_que_parent(point_arrivee, (lon,lat), enfant)]


        liste_rendu.append([(lon,lat), enfants])
    stop = time.time()
    print("temps_ module ", temps)

    print("temps parent_enf", stop - start )
    return liste_rendu

def plus_proche_que_parent(point_arrivee, pos_parent, pos_enfant):
    distance_parent = math.sqrt((point_arrivee[0] - pos_parent[0])**2 + (point_arrivee[1] - pos_parent[1])**2)
    distance_enfant = math.sqrt((point_arrivee[0] - pos_enfant[0])**2 + (point_arrivee[1] - pos_enfant[1])**2)
    return distance_enfant < distance_parent

def polaire(vitesse_vent):
    polaire = pd.read_csv('Sunfast3600.pol', delimiter=r'\s+', index_col=0)
    liste_vitesse = polaire.columns

    #print(f"Vitesse vent demandée : {vitesse_vent}")
    #print(f"Vitesses disponibles dans la polaire : {liste_vitesse}")

    i = 0
    while i < len(liste_vitesse):
        vitesse = float(liste_vitesse[i])
        if vitesse == vitesse_vent:
            return polaire[liste_vitesse[i]]
        elif vitesse > vitesse_vent:
            inf = i - 1
            sup = i
            t = (vitesse_vent - float(liste_vitesse[inf])) / (float(liste_vitesse[sup]) - float(liste_vitesse[inf]))
            return t * polaire[liste_vitesse[inf]] + (1 - t) * polaire[liste_vitesse[sup]]
        i += 1
    print('Erreur vitesse de vent')
    return None


# for i in range(30):
#     print(polaire(12).index)

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

#Pas utile dans le code actuel
def plot_liste_points(liste_points, sous_liste = None, annotate = False):
    x= []
    y = []
    for point in liste_points:
        x.append(point[0])
        y.append(point[1])
    x.append(liste_points[0][0])
    y.append(liste_points[0][1])
    plt.scatter(x,y)
    
    if sous_liste !=None:
        x_sl = [ x[i] for i in sous_liste]
        y_sl = [ y[i] for i in sous_liste]
        
        plt.plot(x_sl,y_sl, color = 'Red')

    if annotate: 
        for idx, (px, py) in enumerate(zip(x, y)):
            plt.annotate(idx, (px, py), textcoords="offset points", xytext=(0,10), ha='center')

    plt.show()

#Pas utile dans le code actuel
def plot_parents_enfants(liste_parents_enfants):
    couleurs = plt.get_cmap('tab20')

    for i, (parent, enfants) in enumerate(liste_parents_enfants):
        couleur = couleurs(i / len(liste_parents_enfants))
        plt.scatter(parent[0], parent[1], color=couleur, s=100, label=f'Parent {i+1}')
        for enfant in enfants:
            plt.scatter(enfant[0], enfant[1], color=couleur, s=50)
            plt.plot([parent[0], enfant[0]], [parent[1], enfant[1]], color=couleur, linestyle='-', linewidth=1)

    plt.legend()
    plt.show()

def orientation(p, q, r):
    """
    Calculer l'orientation du triplet (p, q, r).
    Renvoie 0 si les points sont colinéaires, 1 si dans le sens horaire, 2 si dans le sens antihoraire.
    """
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        return 0
    elif val > 0:
        return 1
    else:
        return 2

def forme_convexe(liste_points):
    """
    Renvoie les points qui se trouvent sur l'enveloppe convexe.
    :param liste_points: Liste de tuples (x, y)
    :return: Liste de points qui sont sur l'enveloppe convexe
    """
    n = len(liste_points)
    if n < 3:
        return []  # Moins de 3 points ne peuvent pas former une enveloppe convexe

    # Trouver le point le plus à gauche
    gauche = 0
    for i in range(1, n):
        if liste_points[i][0] < liste_points[gauche][0]:
            gauche = i

    # Initialiser l'enveloppe convexe
    contour = []
    p = gauche
    while True:
        # Ajouter le point actuel à l'enveloppe
        contour.append(liste_points[p])

        # Trouver le point 'q' tel que l'orientation(p, q, i) est dans le sens antihoraire pour tous les points i
        q = (p + 1) % n
        for i in range(n):
            if orientation(liste_points[p], liste_points[i], liste_points[q]) == 2:
                q = i

        # Maintenant, q est le point le plus à droite du point p
        p = q

        # Boucle jusqu'à ce que l'on revienne au premier point
        if p == gauche:
            break

    return contour

def forme_concave(liste_points, alpha):
    
    """
    Renvoie les points qui se trouvent sur la forme concave (alpha shape).
    :param liste_points: Liste de tuples (x, y)
    :param alpha: Paramètre alpha pour contrôler la "rigidité" de la forme (plus petit = plus concave)
    :return: Liste de points qui sont sur la forme concave
    """
    if len(liste_points) < 4:
        return liste_points  # Moins de 4 points ne peuvent pas former une forme concave utile

    # Créer une forme alpha avec le paramètre alpha
    alpha_shape = alphashape.alphashape(liste_points, alpha)

    # Extraire les points de l'enveloppe de la forme concave
    if isinstance(alpha_shape, Point):
        return [alpha_shape.coords[0]]
    elif isinstance(alpha_shape, MultiPoint):
        return list(alpha_shape.geoms)
    else:
        return list(alpha_shape.exterior.coords)

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

def itere_jusqua_dans_enveloppe(position_initiale, position_finale, lon_grid, lat_grid, u, v, pas_temporel, pas_angle, dist, live = False):
    start_i = time.time()

    temp = pas_temporel
    
    positions = [position_initiale]
    iter_count = 0
    parent_map = {position_initiale: None}  # Pour suivre les relations parent-enfant
    
    if live:
        plt.figure(figsize=(10, 8))
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Itération et Enveloppe Convexe')
        plt.scatter(position_finale[0], position_finale[1], color='black', s=100, marker='*', label='Position Finale')
        plt.grid(True)
        plt.legend()

    while True:
        print(f"Iteration {iter_count}:")
        
        start = time.time()
        liste_parents_enfants = prochains_points_liste_parent_enfants(positions, lon_grid, lat_grid, u, v, temp, pas_angle, True, position_finale)
        stop = time.time()
        print("temps liste_parents_enfants ", stop - start)
        
        points_aplatis = flatten_list(liste_parents_enfants)
        
        enveloppe_concave = forme_concave(points_aplatis,3)#forme_concave(points_aplatis,3.0)

        if live:
            plot_points(liste_parents_enfants, enveloppe_concave, position_finale)
        
        start = time.time()

        # Mettre à jour les relations parent-enfant
        for parent, enfants in liste_parents_enfants:
            for enfant in enfants:
                if enfant not in parent_map:
                    parent_map[enfant] = parent
        
        positions = enveloppe_concave
        print("le nombre de points est : ", len(positions))
        
        if dist_bateau_point(positions, position_finale, 0.01):
            print("validé")
            if temp >= 0.2:
                temp *= 2/3
        
        closest_point = min(points_aplatis, key=lambda point: distance(point, position_finale))
        print(distance(closest_point, position_finale))

        
        if dist_bateau_point(positions, position_finale, dist):
            print("La position finale est maintenant dans l'enveloppe concave.")
            
            # Détermination du point le plus proche de la position finale
            closest_point = min(points_aplatis, key=lambda point: distance(point, position_finale))
            print(f"Le point le plus proche de la position finale est : {closest_point}")
            
            # Tracer le chemin idéal en remontant les relations parent-enfant
            chemin_ideal = []
            current_point = closest_point
            while current_point is not None:
                chemin_ideal.append(current_point)
                current_point = parent_map[current_point]
            
            chemin_ideal.reverse()  # Inverser pour avoir le chemin de l'origine à la destination
            chemin_x, chemin_y = zip(*chemin_ideal)
            
            stop_f = time.time()
            print("temps_total ", stop_f-start_i)
            if not live:
                rv.plot_wind_map(lon_grid, lat_grid, u, v, position_initiale, position_finale,  chemin_x=chemin_x, chemin_y=chemin_y)
            
            if live:      
                plt.plot(chemin_x, chemin_y, color='black', linestyle='-', linewidth=2, label='Chemin Idéal')
                plt.scatter(chemin_x, chemin_y, color='black', s=50)
                plt.show()
                
            
            
            break
        
        iter_count += 1
        stop = time.time()
        print("temps verif ", stop - start)
        
    
    return liste_parents_enfants

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



# Définir les limites de la zone et les paramètres du vent
lon_min, lon_max = -123, -122
lat_min, lat_max = 37, 42
grid_size = 3
wind_strength_range = (10, 15)  # Force du vent en nœuds
wind_angle_range = (0 , 360)  # Angle du vent en degrés

# Générer la carte des vents
lon_grid, lat_grid, u, v = rv.excel2wind_map()

# Tracer la carte des vents
#rv.plot_wind_map(lon_grid, lat_grid, u, v)

# Exemple d'utilisation
position_initiale = (-3, 47)
position_finale = (-3, 48)
pas_temporel = 0.2
pas_angle = 15
itere_jusqua_dans_enveloppe(position_initiale, position_finale, lon_grid, lat_grid, u, v, pas_temporel, pas_angle, 0.01, True)
