import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.path import Path
import alphashape
from shapely.geometry import Point, MultiPoint
import time
import xarray as xr
from cartopy import crs as ccrs, feature as cfeature
import os

import Routage_Vent_en_dev as rv



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
        v_bateau = recup_vitesse_fast(pol_v_vent, d_vent - angle)
        liste_points.append(projection(position, angle, v_bateau * pas_temporel))
    stop = time.time()
    #print(stop - start)
    return liste_points

def prochains_points_liste_parent_enfants(liste, pas_temporel, pas_angle, filtrer_par_distance=False, point_arrivee=None, heure = 0):
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
    liste_rendu = []

    temps = 0
    temps2 = 0
    for lon,lat in liste:
        #lon, lat = parent
        # Obtenir la direction et la force du vent pour la position actuelle      
        start1 = time.time()
        v_vent, d_vent = rv.get_wind_from_grib(lat, lon, heure)

        stop1 = time.time()
        temps += (stop1 - start1)

        start2 = time.time()
        pol_v_vent = polaire(v_vent)
        stop2 = time.time()
        temps2 += stop2 - start2

        enfants = prochains_points((lon,lat), pol_v_vent, d_vent, pas_temporel, pas_angle)

        
        

        # Filtrer les enfants selon la distance au point d'arrivée
        if filtrer_par_distance and point_arrivee is not None:
            enfants = [enfant for enfant in enfants if plus_proche_que_parent(point_arrivee, (lon,lat), enfant)] #and not rv.is_on_land(enfant[0], enfant[1])]


        liste_rendu.append([(lon,lat), enfants])
    #print("temps_ get_wind ", temps)
    #print("temps polaire", temps2)

    return liste_rendu

def plus_proche_que_parent(point_arrivee, pos_parent, pos_enfant):
    distance_parent = math.sqrt((point_arrivee[0] - pos_parent[0])**2 + (point_arrivee[1] - pos_parent[1])**2)
    distance_enfant = math.sqrt((point_arrivee[0] - pos_enfant[0])**2 + (point_arrivee[1] - pos_enfant[1])**2)
    return distance_enfant < distance_parent

def polaire(vitesse_vent):
    polaire = pd.read_csv('Sunfast3600.pol', delimiter=r'\s+', index_col=0)
    liste_vitesse = polaire.columns

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

def itere_jusqua_dans_enveloppe(position_initiale, position_finale, pas_temporel, pas_angle, dist, live = False, enregistrement = True):
    
    heure = 0
    
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
        print('Heure ', heure)
        
        start = time.time()
        liste_parents_enfants = prochains_points_liste_parent_enfants(positions, temp, pas_angle, True, position_finale, heure = heure)
        stop = time.time()

        heure += pas_temporel
        print("temps liste_parents_enfants ", stop - start)
        
        points_aplatis = flatten_list(liste_parents_enfants)
        
        enveloppe_concave = forme_concave(points_aplatis,5)

        if live:
            plot_points(liste_parents_enfants, enveloppe_concave, position_finale)
        
        # Mettre à jour les relations parent-enfant
        for parent, enfants in liste_parents_enfants:
            for enfant in enfants:
                if enfant not in parent_map:
                    parent_map[enfant] = parent
        
        positions = enveloppe_concave
        print("le nombre de points est : ", len(positions))
        
        if dist_bateau_point(positions, position_finale, 0.01):
            print("validé")
            if temp >= 0.5:
                temp *= 2/3
        
        closest_point = min(points_aplatis, key=lambda point: distance(point, position_finale))
        print('distance arrivée, point_plus_proche ', distance(closest_point, position_finale))

        
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
                pass
                rv.plot_wind(chemin_x=chemin_x, chemin_y=chemin_y)
            
            if live:      
                plt.plot(chemin_x, chemin_y, color='black', linestyle='-', linewidth=2, label='Chemin Idéal')
                plt.scatter(chemin_x, chemin_y, color='black', s=50)
                plt.show()
                
            
            break
        
        iter_count += 1
    
    if enregistrement == True:
        lien_dossier = r"C:\Users\arthu\OneDrive\Arthur\Programmation\TIPE_Arthur_Lhoste\route_ideale"
        rv.enregistrement_route(chemin_x, chemin_y, pas_temporel, output_dir=lien_dossier)    
    
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

