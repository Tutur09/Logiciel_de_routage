import Logicielroutage_en_dev as lr
import Routage_Vent_en_dev as rv
import os

#Choisir la localisation de navigation
loc_nav = [-5.45, -1.6, 47.2 , 49]

position_initiale, position_finale = rv.point_ini_fin(loc_nav)

pas_temporel = 3
pas_angle = 15

#Chemin d'accès du fichier GRIB    
file_path = os.path.join('Logiciel', 'Données_vent', 'METEOCONSULT12Z_VENT_0925_Gascogne.grb')

lr.itere_jusqua_dans_enveloppe(position_initiale, position_finale, pas_temporel, pas_angle, 0.5, loc_nav, live = False, enregistrement = False)  