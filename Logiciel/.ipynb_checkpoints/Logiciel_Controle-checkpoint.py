import Logicielroutage_en_dev as lr
import Routage_Vent_en_dev as rv

# Choisir la localisation de navigation
bg = (43.27750727162645, -9.84229985332882)
hd = (48.73899721806831, -0.25559581307713825)
loc_nav = [bg[1], hd[1], bg[0], hd[0]]



position_initiale, position_finale = rv.point_ini_fin(loc_nav)

# position_initiale, position_finale = ((-3.0620315398886806, 47.02309833024118), (-7.679471243042671, 45.13877551020408))

pas_temporel = 1
pas_angle = 10

# Chemin d'accès du fichier GRIB    
lr.itere_jusqua_dans_enveloppe(position_initiale, position_finale, pas_temporel, pas_angle, 0.3, loc_nav, live = True, enregistrement = False)  