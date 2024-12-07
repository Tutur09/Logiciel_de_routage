import Logicielroutage as lr
import Routage_Vent as rv

import pandas as pd


def get_indice_position(x, y):
    data = pd.read_excel(excel_file, header=None)

def prochains_points(position, pol_v_vent, d_vent, pas_temporel, pas_angle):
    liste_points = []

    chemin = list(range(0, 360, pas_angle))
    for angle in chemin:
        v_bateau = recup_vitesse_fast(pol_v_vent, d_vent - angle)
        liste_points.append(projection(position, angle, v_bateau * pas_temporel))

    return liste_points