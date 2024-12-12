import Paramètres as p
import Routage_Vent as rv
import Logicielroutage as lr
import numpy as np
import matplotlib.pyplot as plt

class Bateau:
    def __init__(self, lat, lon, orientation=0, taille=0.1):
        """
        Initialise un bateau avec :
        - lat, lon : coordonnées de la position.
        - orientation : angle de direction initiale (en degrés, 0 = nord).
        - taille : taille relative du triangle représentant le bateau.
        """
        self.lat = lat
        self.lon = lon
        self.orientation = orientation  # Orientation en degrés
        self.taille = taille  # Taille relative du bateau
        self.vitesse = 0  # Vitesse actuelle (sera calculée)
        self.historique_positions = [(lon, lat)]  # Historique des positions

    def triangle(self):
        """
        Génère les coordonnées des sommets du triangle représentant le bateau.
        """
        orientation_rad = np.radians(self.orientation)
        demi_base = self.taille / 2
        hauteur = self.taille

        proue = (self.lon + hauteur * np.cos(orientation_rad), 
                 self.lat + hauteur * np.sin(orientation_rad))
        
        arriere_gauche = (self.lon - demi_base * np.cos(orientation_rad - np.pi / 2),
                          self.lat - demi_base * np.sin(orientation_rad - np.pi / 2))
        
        arriere_droit = (self.lon - demi_base * np.cos(orientation_rad + np.pi / 2),
                         self.lat - demi_base * np.sin(orientation_rad + np.pi / 2))

        return [proue, arriere_gauche, arriere_droit]

    def afficher(self, ax=None):
        """
        Affiche le bateau sous forme d'un triangle sur un graphique matplotlib.
        """
        triangle_coords = self.triangle()
        x_coords, y_coords = zip(*(triangle_coords + [triangle_coords[0]]))  # Boucler le triangle
        
        if ax is None:
            _, ax = plt.subplots()
        
        ax.plot(x_coords, y_coords, 'b-', label="Bateau")  # Dessiner le triangle
        ax.fill(x_coords, y_coords, color='blue', alpha=0.3)  # Colorier l'intérieur
        ax.scatter(self.lon, self.lat, color='red', label="Centre du bateau")  # Position centrale
        ax.legend()
        ax.set_aspect('equal')
        ax.set_title("Représentation du bateau")
        plt.show()

    def avancer(self, pas_temporel, reseau):
        """
        Fait avancer le bateau en utilisant un réseau de neurones pour prédire l'orientation.
        """
        # Récupérer les conditions de vent à la position actuelle
        vitesse_vent, angle_vent = rv.get_wind_at_position(self.lat, self.lon, time_step=p.heure_debut)
        
        # Préparer l'entrée pour le réseau de neurones
        entree_nn = np.array([[vitesse_vent, angle_vent, self.orientation]])
        angle_pred = reseau.predict(entree_nn)[0]  # Corrige l'accès au résultat

        # Ajuster l'orientation et calculer le déplacement
        self.orientation = angle_pred
        polaire = lr.polaire(vitesse_vent)
        self.vitesse = lr.recup_vitesse_fast(polaire, angle_vent - self.orientation)
        delta_distance = self.vitesse * pas_temporel
        prochain_point = lr.projection((self.lon, self.lat), self.orientation, delta_distance)
        self.lon, self.lat = prochain_point
        self.historique_positions.append((self.lon, self.lat))


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le bateau à la position initiale
    bateau = Bateau(lat=p.position_initiale[1], lon=p.position_initiale[0], orientation=90, taille=0.5)

    for _ in range(10):  # Exemple : avancer 10 étapes
        bateau.avancer(p.pas_temporel, )
        bateau.afficher()
