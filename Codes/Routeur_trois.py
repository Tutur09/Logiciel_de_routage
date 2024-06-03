import numpy as np
import math

import matplotlib.pyplot as plt

import pandas as pd
import cartopy.crs as ccrs
import cartopy.feature as cfeature


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

def prochains_points(position, v_vent, d_vent, pas_temporel, pas_angle):
    liste_points = []
    chemin = list(range(0, 360, pas_angle))
    for angle in chemin:
        v_bateau = recup_vitesse(v_vent, d_vent - angle)
        liste_points.append(projection(position, angle, v_bateau * pas_temporel))
    return liste_points, chemin  

def prochains_points_liste(liste,liste_chemin, v_vent, d_vent, pas_temporel, pas_angle):
    liste_rendu = []
    print('liste points',liste)
    print('liste chemin',liste_chemin)
    liste_nouveaux_chemins = []
    for i in range(len(liste)):
        print(i)
        point = liste[i]
        chemin = liste_chemin[i]
        nouveaux_points , nouveau_chemin = prochains_points(point, v_vent, d_vent, pas_temporel, pas_angle)
        print('Nouveau chemin',nouveau_chemin)
        chemins_complets =  [ chemin + [nouveau_chemin[j]] for j in range(len(nouveau_chemin))]
        print('Chemin complet',chemins_complets)
        liste_rendu += nouveaux_points
        liste_nouveaux_chemins += chemins_complets
    print(f'{len(liste_rendu)} vs {len(liste_nouveaux_chemins)}')
    print(liste_nouveaux_chemins)
    return liste_rendu, liste_nouveaux_chemins

    
def polaire(vitesse_vent):
    """_summary_

    Args:
        vitesse_vent (float): _description_

    Returns:
        _type_: _description_
    """
    polaire = pd.read_csv('C:/Users/arthu/OneDrive/Arthur/Programmation/TIPE/Sunfast3600.pol', delimiter=r'\s+', index_col=0)
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
            
def plot_liste_points(liste_points, sous_liste = None):
    x= []
    y = []
    for point in liste_points:
        x.append(point[0])
        y.append(point[1])
    x.append(liste_points[0][0])
    y.append(liste_points[0][1])
    plt.scatter(x,y)
    
     
    # Annotating all points with their indices
    for idx, (px, py) in enumerate(zip(x, y)):
        plt.annotate(idx, (px, py), textcoords="offset points", xytext=(0,10), ha='center')

    if sous_liste !=None:
        x_sl = [ x[i] for i in sous_liste]
        y_sl = [ y[i] for i in sous_liste]
        
        plt.plot(x_sl,y_sl, color = 'Red')
        
    plt.show()

def plot_avancement(avancement):
    for liste_points in avancement:
        x= []
        y = []
        for point in liste_points:
            x.append(point[0])
            y.append(point[1])
        x.append(liste_points[0][0])
        y.append(liste_points[0][1])
        plt.plot(x,y)
    plt.show()
                
def forme_convexe(liste_points):
    x = []
    y = []
    for point in liste_points:
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

def forme_concave(liste_points,alpha=140):
    contour_convexe = forme_convexe(liste_points)
    # contour = []
    # for i in range(1,len(contour_convexe)):
    #     contour.append(contour_convexe[i-1])
    #     print(f"Ajout {contour_convexe[i-1]} de l'enveloppe convexe")
    #     for j in range(len(liste_points)):
    #         if j not in contour_convexe:
    #             vec1_x = liste_points[contour_convexe[i-1]][0]-liste_points[j][0]
    #             vec1_y = liste_points[contour_convexe[i-1]][1]-liste_points[j][1]
    #             vec2_x = liste_points[contour_convexe[i]][0]-liste_points[j][0]
    #             vec2_y = liste_points[contour_convexe[i]][1]-liste_points[j][1]
    #             vec1_long = math.sqrt(vec1_x**2 + vec1_y**2)
    #             vec2_long = math.sqrt(vec2_x**2 + vec2_y**2)
                
    #             scal = vec1_x * vec2_x + vec1_y * vec2_y
    #             if vec1_long ==0 or vec2_long ==0:
    #                 print('Erreur')
    #             angle = math.degrees(math.acos(scal / (vec1_long * vec2_long)))
                
    #             if angle > alpha:
    #                 contour.append(j)
    #                 print(f'Ajout {j} entre {contour_convexe[i-1]} et {contour_convexe[i]} ')
    return contour_convexe #Pour l'instant


# Example usage:
long_ini = -122.431297
lat_ini = 37.773972
position = (long_ini, lat_ini)
avancement = [[ position]]
chemins = [[['Début']]]
for i in range(3):
    print('Iter',i)
    liste_points, nouveaux_chemins = prochains_points_liste(avancement[-1],chemins[-1], 13 + 2*i , 45 + 20*i, 1, 120)
    forme_conc = forme_concave(liste_points,140)
    print(forme_conc)
    plot_liste_points(liste_points, forme_conc)
    liste_points2 = [ (liste_points[j][0],liste_points[j][1]) for j in forme_conc]
    nouveaux_chemins2 = [ nouveaux_chemins[j] for j in forme_conc]
    avancement += [liste_points2]
    print('nouveau chemin',nouveaux_chemins2)
    chemins += nouveaux_chemins2
    print('Chemins',chemins)
    

print(avancement)
plot_avancement(avancement)