import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd

def projection(position, cap, distance):
    """Project a new position based on initial position, heading (cap), and distance."""
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


def prochains_points(position, pol, d_vent, pas_temporel, pas_angle):
    """Generate new points based on the current position, wind data, and time step."""
    liste_points = []
    chemin = list(range(0, 360, pas_angle))
    for angle in chemin:
        v_bateau = recup_vitesse_fast(pol, d_vent - angle)
        liste_points.append(projection(position, angle, v_bateau * pas_temporel))
    return liste_points


def prochains_points_liste(liste, v_vent, d_vent, pas_temporel, pas_angle):
    """Generate a list of new points for each point in the input list."""
    pol = polaire(v_vent)
    liste_rendu = []
    for point in liste:
        nouveaux_points = prochains_points(point, pol, d_vent, pas_temporel, pas_angle)
        # Connect each new set of points to its parent point
        liste_rendu.append((point, nouveaux_points))
    return liste_rendu


def polaire(vitesse_vent):
    """Retrieve wind speed polar data."""
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


def recup_vitesse_fast(pol, angle):
    """Retrieve wind speed based on angle."""
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
            inf = i - 1
            sup = i
            t = (angle - float(liste_angle[inf])) / (float(liste_angle[sup]) - float(liste_angle[inf]))
            return t * pol[liste_angle[inf]] + (1 - t) * pol[liste_angle[sup]]
        i += 1
    print('Erreur angle')
    return None


def plot_liste_points(liste_points, sous_liste=None, annotate=False):
    """Plot the list of points and optionally annotate them."""
    x = []
    y = []
    for point in liste_points:
        x.append(point[0])
        y.append(point[1])

    plt.plot(x, y, marker='o')  # Connect points with lines

    if sous_liste is not None:
        x_sl = [x[i] for i in sous_liste]
        y_sl = [y[i] for i in sous_liste]
        plt.plot(x_sl, y_sl, color='Red')

    if annotate:
        for idx, (px, py) in enumerate(zip(x, y)):
            plt.annotate(idx, (px, py), textcoords="offset points", xytext=(0, 10), ha='center')

    plt.show()


def forme_convexe(liste_points):
    """Find the convex hull of the list of points."""
    x = [point[0] for point in liste_points]
    y = [point[1] for point in liste_points]

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
                if vecteur_x != 0 or vecteur_y != 0:
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


long_ini = -122.431297
lat_ini = 37.773972
position = (long_ini, lat_ini)  # Ensure position is correctly initialized as a tuple

avancement = [position]
tracer = [position]

for i in range(2):
    parent_points = avancement[-1]
    liste_points = prochains_points_liste(parent_points, 13, 0, 0.5, 10)
    
    # Extract the new points forming the convex hull
    liste_points2 = []
    for parent, points in liste_points:
        forme_conc = forme_convexe(points)
        liste_points2 += [(points[j][0], points[j][1]) for j in forme_conc]

    # Append the new set of points to avancement
    avancement += liste_points2
    
    # Extend tracer with the newly added points
    tracer += liste_points2
    
    print(i)

plot_liste_points(tracer)
print(avancement)
