import numpy as np
import math

import matplotlib.pyplot as plt

import pandas as pd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import time
from multiprocessing import Pool



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

def projection_vectorized(positions, caps, distances):
    # Earth radius in nautical miles
    R = 3440.0
    
    # Convert latitude and longitude from degrees to radians
    lat_ini_rad = np.radians(positions[:, 1])
    long_ini_rad = np.radians(positions[:, 0])
    
    # Convert bearing to radians
    bearing_rad = np.radians(caps)
    
    # Distance ratio compared to the earth's radius
    distance_ratio = distances / R
    
    # Calculate new latitude in radians
    new_lat_rad = np.arcsin(np.sin(lat_ini_rad) * np.cos(distance_ratio) + 
                            np.cos(lat_ini_rad) * np.sin(distance_ratio) * np.cos(bearing_rad))
    
    # Calculate new longitude in radians
    new_long_rad = long_ini_rad + np.arctan2(np.sin(bearing_rad) * np.sin(distance_ratio) * np.cos(lat_ini_rad),
                                             np.cos(distance_ratio) - np.sin(lat_ini_rad) * np.sin(new_lat_rad))
    
    # Convert new latitude and longitude to degrees
    new_lat = np.degrees(new_lat_rad)
    new_long = np.degrees(new_long_rad)
    
    return np.column_stack((new_long, new_lat))

def prochains_points(position, pol, d_vent, pas_temporel, pas_angle):
    liste_points = []
    chemin = list(range(0, 360, pas_angle))
    for angle in chemin:

        v_bateau = recup_vitesse_fast(pol, d_vent - angle)
        liste_points.append(projection(position, angle, v_bateau * pas_temporel))
    return liste_points

def prochains_points_liste(liste, v_vent, d_vent, pas_temporel, pas_angle):
    pol = polaire(v_vent)
    liste_rendu = []
    for i in range(len(liste)):
        point = liste[i]
        nouveaux_points = prochains_points(point, pol, d_vent, pas_temporel, pas_angle)
        liste_rendu += nouveaux_points
    return liste_rendu

def prochains_points_liste_parent_enfants(liste, v_vent, d_vent, pas_temporel, pas_angle, filtrer_par_distance=False, point_arrivee=None):
    """
    Génère des sous-listes de parents et d'enfants pour chaque point parent.
    Filtre les enfants en fonction de leur proximité avec le point d'arrivée si spécifié.

    Args:
        liste (list): Liste des positions parents.
        v_vent (float ou integer): Vitesse du vent.
        d_vent (float ou integer): Direction du vent.
        pas_temporel (float ou integer): Intervalle de temps entre les itérations.
        pas_angle (float ou integer): Incrément d'angle pour la génération des points.
        filtrer_par_distance (bool): Activer le filtrage basé sur la distance si True.
        point_arrivee (tuple): La position finale (longitude, latitude).

    Returns:
        list: Liste avec des sous-listes parents/enfants.
    """
    pol = polaire(v_vent)
    liste_rendu = []

    for i in range(len(liste)):
        parent = liste[i]
        enfants = prochains_points(parent, pol, d_vent, pas_temporel, pas_angle)

        # Filtrer les enfants selon la distance au point d'arrivée
        if filtrer_par_distance and point_arrivee is not None:
            enfants = [enfant for enfant in enfants if plus_proche_que_parent(point_arrivee, parent, enfant)]

        liste_rendu.append([parent, enfants])
    return liste_rendu

def plus_proche_que_parent(point_arrivee, pos_parent, pos_enfant):
    """
    Vérifie si l'enfant est plus proche du point d'arrivée que le parent.

    Args:
        point_arrivee (tuple): Position du point d'arrivée (longitude, latitude).
        pos_parent (tuple): Position du parent (longitude, latitude).
        pos_enfant (tuple): Position de l'enfant (longitude, latitude).

    Returns:
        bool: True si l'enfant est plus proche que le parent, sinon False.
    """
    distance_parent = math.sqrt((point_arrivee[0] - pos_parent[0])**2 + (point_arrivee[1] - pos_parent[1])**2)
    distance_enfant = math.sqrt((point_arrivee[0] - pos_enfant[0])**2 + (point_arrivee[1] - pos_enfant[1])**2)
    return distance_enfant < distance_parent

 
def polaire(vitesse_vent):
    """_summary_

    Args:
        vitesse_vent (float): _description_

    Returns:
        _type_: _description_
    """
    polaire = pd.read_csv('Sunfast3600.pol', delimiter=r'\s+', index_col=0)
    liste_vitesse = polaire.columns

    i=0
    while i<len(liste_vitesse):
        vitesse = float(liste_vitesse[i])
        if vitesse == vitesse_vent:
            return polaire[liste_vitesse[i]]
        elif vitesse > vitesse_vent:
            inf = i-1
            sup = i
            t = (vitesse_vent - float(liste_vitesse[inf])) / (float(liste_vitesse[sup]) - float(liste_vitesse[inf]))
            return t * polaire[liste_vitesse[inf]] + (1 - t) * polaire[liste_vitesse[sup]]
        i+=1
    print('Erreur vitesse de vent')
    return None
        
def recup_vitesse(vitesse_vent, angle): #Renvoie la vitesse pour un angle et vent donné
    """_summary_

    Args:
        vitesse_vent (float): _description_
        angle (float): _description_

    Returns:
        _type_: _description_
    """
    pol = polaire(vitesse_vent)
    angle = abs(angle)
    if angle > 180:
        angle = 360 - angle
    
    liste_angle = pol.index
    
    i = 0
    while i < len(pol):
        angle_vent = float(liste_angle[i])
        if angle == angle_vent:
            return pol[liste_angle[i]]
        elif angle_vent > angle:
            inf = i-1
            sup = i
            t = (angle - float(liste_angle[inf])) / (float(liste_angle[sup]) - float(liste_angle[inf]))
            return t * pol[liste_angle[inf]] + (1 - t) * pol[liste_angle[sup]]
        i+=1
    print('Erreur angle')
    return None

def recup_vitesse_fast(pol, angle): #Renvoie la vitesse pour un angle et vent donné
    """_summary_

    Args:
        vitesse_vent (float): _description_
        angle (float): _description_

    Returns:
        _type_: _description_
    """
    angle = abs(angle)
    if angle > 180:
        angle = 360 - angle
    
    liste_angle = pol.index
    
    i = 0
    while i < len(pol):
        angle_vent = float(liste_angle[i])
        if angle == angle_vent:
            return pol[liste_angle[i]]
        elif angle_vent > angle:
            inf = i-1
            sup = i
            t = (angle - float(liste_angle[inf])) / (float(liste_angle[sup]) - float(liste_angle[inf]))
            return t * pol[liste_angle[inf]] + (1 - t) * pol[liste_angle[sup]]
        i+=1
    print('Erreur angle')
    return None
            
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
        # Annotating all points with their indices
        for idx, (px, py) in enumerate(zip(x, y)):
            plt.annotate(idx, (px, py), textcoords="offset points", xytext=(0,10), ha='center')

        
    plt.show()

def plot_deux_listes(liste1, liste2):
    x1, y1, x2, y2= [], [], [], []
    for point in liste1:
        x1.append(point[0])
        y1.append(point[1])
    x1.append(liste1[0][0])
    y1.append(liste1[0][1])
    
    for point in liste2:
        x2.append(point[0])
        y2.append(point[1])
    x2.append(liste2[0][0])
    y2.append(liste2[0][1])
    
    plt.scatter(x2, y2, color='blue', label='Itération 2')
    plt.scatter(x1, y1, color='red', label='Itération 1')
    
    plt.legend()
    
    plt.show()
     
def plot_parents_enfants(liste_parents_enfants):
    """
    Trace tous les points tels que le parent a la même couleur que ses enfants
    et les relie par des traits.

    Args:
        liste_parents_enfants (list): Liste de sous-listes où chaque sous-liste contient un parent et ses enfants.
    """
    # Générer une palette de couleurs avec plus de diversité
    couleurs = plt.get_cmap('tab20')

    for i, (parent, enfants) in enumerate(liste_parents_enfants):
        couleur = couleurs(i / len(liste_parents_enfants))

        # Tracer le parent avec une taille de point plus grande
        plt.scatter(parent[0], parent[1], color=couleur, s=100, label=f'Parent {i+1}')

        # Tracer les enfants avec une taille de point standard et dessiner des lignes vers le parent
        for enfant in enfants:
            plt.scatter(enfant[0], enfant[1], color=couleur, s=50)
            plt.plot([parent[0], enfant[0]], [parent[1], enfant[1]], color=couleur, linestyle='-', linewidth=1)

    # Ajouter une légende pour identifier chaque parent
    plt.legend()

    # Afficher le graphique
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

def flatten_list(nested_list):
    """
    Prend une liste potentiellement imbriquée d'éléments et renvoie une liste avec tous 
    les éléments dépliés.

    Args:
        nested_list (list): La liste potentiellement imbriquée d'éléments.

    Returns:
        list: Une liste contenant tous les éléments dépliés.
    """
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
    """
    Vérifie si un point est dans l'enveloppe convexe donnée.

    Args:
        point (tuple): Le point à vérifier (x, y).
        hull (list): Liste de points qui forment l'enveloppe convexe.

    Returns:
        bool: True si le point est dans l'enveloppe, sinon False.
    """
    hull_path = np.array(hull)
    from matplotlib.path import Path
    path = Path(hull_path)
    return path.contains_point(point)

def itere_jusqua_dans_enveloppe(position_initiale, position_finale, v_vent, d_vent, pas_temporel, pas_angle):
    """
    Itère jusqu'à ce que la position finale soit incluse dans l'enveloppe convexe des points générés.

    Args:
        position_initiale (tuple): La position initiale (longitude, latitude).
        position_finale (tuple): La position finale (longitude, latitude).
        v_vent (float): Vitesse du vent.
        d_vent (float): Direction du vent.
        pas_temporel (float): Intervalle de temps entre les itérations.
        pas_angle (int): Incrément d'angle pour la génération des points.

    Returns:
        list: Liste des itérations où chaque itération est une liste de parents et enfants.
    """
    positions = [position_initiale]
    iter_count = 0

    # Initialiser le graphique
    plt.figure(figsize=(10, 8))
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Itération et Enveloppe Convexe')
    plt.scatter(position_finale[0], position_finale[1], color='black', s=100, marker='*', label='Position Finale')
    plt.grid(True)
    plt.legend()

    while True:
        print(f"Iteration {iter_count}:")
        liste_parents_enfants = prochains_points_liste_parent_enfants(positions, v_vent, d_vent, pas_temporel, pas_angle,True, position_finale)
        
        # Aplatir la liste des points générés
        points_aplatis = flatten_list(liste_parents_enfants)
        
        # Obtenez l'enveloppe convexe des points générés
        enveloppe_convexe = forme_convexe(points_aplatis)

        # Tracer les points de l'itération actuelle
        plot_points(liste_parents_enfants, enveloppe_convexe, position_finale)
        
        # Vérifiez si la position finale est dans l'enveloppe convexe
        if is_point_in_hull(position_finale, enveloppe_convexe):
            print("La position finale est maintenant dans l'enveloppe convexe.")
            plt.pause(2)  # Pause pour voir le résultat final
            break
        
        # Mettre à jour les positions pour la prochaine itération
        positions = enveloppe_convexe
        iter_count += 1
    
    return liste_parents_enfants

def plot_points(liste_parents_enfants, enveloppe_convexe, position_finale):
    """
    Trace tous les points des parents et enfants ainsi que l'enveloppe convexe et la position finale.

    Args:
        liste_parents_enfants (list): Liste de sous-listes où chaque sous-liste contient un parent et ses enfants.
        enveloppe_convexe (list): Liste de points formant l'enveloppe convexe.
        position_finale (tuple): La position finale (longitude, latitude).
    """
    couleurs = plt.get_cmap('tab20')
    for i, (parent, enfants) in enumerate(liste_parents_enfants):
        couleur = couleurs(i / len(liste_parents_enfants))
        plt.scatter(parent[0], parent[1], color=couleur, s=100, label=f'Parent {i+1}')
        for enfant in enfants:
            plt.scatter(enfant[0], enfant[1], color=couleur, s=50)
            plt.plot([parent[0], enfant[0]], [parent[1], enfant[1]], color=couleur, linestyle='-', linewidth=1)

    # Tracer l'enveloppe convexe
    if len(enveloppe_convexe) > 0:
        hull_x, hull_y = zip(*enveloppe_convexe)
        plt.plot(hull_x + (hull_x[0],), hull_y + (hull_y[0],), 'r--', lw=2, label='Enveloppe Convexe')

    # Mettre à jour le graphique
    plt.pause(0.5)  # Pause pour permettre à l'affichage d'être interactif

# Exemple d'utilisation
position_initiale = (-122.431297, 37.773972)
position_finale = (-122.5, 40.8)
v_vent = 10
d_vent = 90
pas_temporel = 5
pas_angle = 20

itere_jusqua_dans_enveloppe(position_initiale, position_finale, v_vent, d_vent, pas_temporel, pas_angle)

# # Example usage:
# long_ini = -122.431297
# lat_ini = 37.773972
# position = (long_ini, lat_ini)
# avancement = [[ position]]
# pred = [[[0]]]

# #print([position])
# #print("******************************")
# liste1 = prochains_points_liste_parent_enfants([position], 10, 0, 1, 20)
# #print(liste1)

# plot_parents_enfants(liste1)
# #Il faut transformer liste1 en une grosse liste
# liste1_bis = flatten_list(liste1)

# liste1_tri = forme_convexe(liste1_bis)

# liste2 = prochains_points_liste_parent_enfants(liste1_tri, 10, 0, 1, 20)
# print("liste parent/enfants : ", liste2)

# plot_parents_enfants(liste2)

# liste2_bis = flatten_list(liste2)
# liste2_tri = forme_convexe(liste2_bis)

# liste3 = prochains_points_liste_parent_enfants(liste2_tri, 10, 45, 1, 20)
# plot_parents_enfants(liste3)

# liste3_bis = flatten_list(liste3)
# liste3_tri = forme_convexe(liste3_bis)

# liste4 = prochains_points_liste_parent_enfants(liste3_tri, 10, 120, 1, 20)
# plot_parents_enfants(liste4)
