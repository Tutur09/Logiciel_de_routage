import Logicielroutage_en_dev as lr
import Routage_Vent_en_dev as rv

# Choisir la localisation de navigation
loc_nav = [-5.674665036886783, -2.508547080563329, 47.091821997818506, 49.05178524339951]


position_initiale, position_finale = rv.point_ini_fin(loc_nav)

# position_initiale, position_finale = ((-3.0620315398886806, 47.02309833024118), (-7.679471243042671, 45.13877551020408))

pas_temporel = 0.3
pas_angle = 20

# Chemin d'accès du fichier GRIB    
lr.itere_jusqua_dans_enveloppe(position_initiale, position_finale, pas_temporel, pas_angle, 0.5, loc_nav, live = False, enregistrement = False)  