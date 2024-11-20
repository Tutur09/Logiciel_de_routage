import Logicielroutage_en_dev as lr
import Routage_Vent_en_dev as rv
import os

#Choisir la localisation de navigation
loc_nav = [-10.6, -0.73, 42.4 , 48.5]

#position_initiale, position_finale = rv.point_ini_fin(loc_nav)

position_initiale, position_finale = ((-3.0620315398886806, 47.02309833024118), (-7.679471243042671, 45.13877551020408))

pas_temporel = 3
pas_angle = 30

#Chemin d'accès du fichier GRIB    
file_path = os.path.join('Logiciel', 'Données_vent', 'METEOCONSULT00Z_VENT_1110_Gascogne_départ_vendée.grb')

lr.itere_jusqua_dans_enveloppe(position_initiale, position_finale, pas_temporel, pas_angle, 0.5, loc_nav, live = False, enregistrement = False)  