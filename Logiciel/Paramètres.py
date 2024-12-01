#PARAMETRES LOGICIEL_CONTROLE
position_initiale, position_finale = ((-3.0620315398886806, 47.02309833024118), (-7.679471243042671, 45.13877551020408))

bg = (33.0434624891455, -78.75562797102944)
hd = (66.11535743422027, 6.991309094387126)
loc_nav = [bg[1], hd[1], bg[0], hd[0]]

pas_temporel = 3
pas_angle = 15
tolerance_arrivée = 0.3

enregistrement = False
live = True

# PARAMETRES ROUTAGE_VENT
land = r'Logiciel\Carte_frontières_terrestre\ne_10m_land.shp'
vent = r'Logiciel\Données_vent\METEOCONSULT12Z_VENT_1201_Nord_Atlantique.grb'
excel_wind = r'Logiciel\Données_vent\Vent.xlsx'

type = 'grib'

output_dir = r'C:\Users\arthu\OneDrive\Arthur\Programmation\TIPE_Arthur_Lhoste\images_png'

# PARAMETRES LOGICIEL_ROUTAGE
delimeter = r';'  # r'\s+' si Sunfastpol sinon r';'  pour Imoca 
polaire = r'Logiciel\Imoca2.pol'

heure_debut = 0
alpha = 3
tolerance = 0.01

land_contact = False 


source_vent = 'grib'