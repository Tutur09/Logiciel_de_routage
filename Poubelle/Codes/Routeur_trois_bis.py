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
        liste_points.append((projection(position, angle, v_bateau * pas_temporel), position))
    return liste_points


def prochains_points_liste(liste, v_vent, d_vent, pas_temporel, pas_angle):
    pol = polaire(v_vent)
    liste_rendu = []
    for point in range(len(liste)):
        nouveaux_points = prochains_points(point, pol, d_vent, pas_temporel, pas_angle)
        liste_rendu += (nouveaux_points, point) #On rend un tuple pour connaitre le parent de ce point afin de les relier
    return liste_rendu



    
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

                
def forme_convexe(liste_points):
    x = []
    y = []
    for point in liste_points[0]:
        x.append(point[0])
        y.append(point[1])
    # Finding the point with the minimum x to start with
    gauche = x.index(min(x))
    contour = [gauche]
    direction = 0  # Initial direction is 0 radians
    fini = False

    while not fini:
        angle_mini = float('inf')  # Start with the largest possible float
        nouveau_point = None

        for i in range(len(liste_points)):
            if i != contour[-1]:  # Make sure we do not calculate the angle to itself
                vecteur_x = liste_points[i][0] - liste_points[contour[-1]][0]
                vecteur_y = liste_points[i][1] - liste_points[contour[-1]][1]
                if vecteur_x!=0 or vecteur_y!=0:
                    angle = math.atan2(vecteur_x, vecteur_y)  
                    angle_diff = (angle - direction) % (2 * math.pi)  # Correct for angle wrapping

                    if angle_diff < angle_mini:
                        angle_mini = angle_diff
                        nouvelle_direction = angle
                        nouveau_point = i

        contour.append(nouveau_point)
        direction = nouvelle_direction
        if nouveau_point == contour[0] and len(contour) > 1:
            fini = True

    return contour

def vent_position(grib):
    
    pass


# Example usage:

matrice_vent = [[(10 ,  0), (10 , 10), (10 ,  7), (10 , 7)],
                [(10 ,  8), (10 , 30), (10 , 20), (10 , 1)],
                [(10 , 25), (10 , 24), (10 , 13), (10 , 1)],
                [(10 , 50), (10 , 11), (10 , 18), (10 , 5)]]

long_ini = -122.431297
lat_ini = 37.773972
position = (long_ini, lat_ini)
avancement = [[ position]]
pred = [[[0]]]
chemins = [[['Début']]]
for i in range(5):
    print('Iter',i)

    temps_début = time.time()

    liste_points = prochains_points_liste(avancement[-1], 13 , 0, 0.5, 20)
    forme_conc = forme_convexe(liste_points)
    temps_fin = time.time()

    temps_exécution = temps_fin - temps_début
    print(f"Temps d'exécution : {temps_exécution} secondes")

    liste_points2 = [ (liste_points[j][0],liste_points[j][1]) for j in forme_conc]
    plot_liste_points(liste_points,forme_conc)
    avancement += [liste_points2]
    
    

print(avancement)

