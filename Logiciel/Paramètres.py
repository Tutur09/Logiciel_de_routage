# PARAMETRES LOGICIEL_CONTROLE
"TRAVERSEE ATLANTIQUE"
position_initiale, position_finale = ((-3.7459774441825315, 45.608997661941785), (-60.31512438218373, 39.21922058302923))
bg = (35.0434624891455, -78.75562797102944)
hd = (66.11535743422027, 6.991309094387126)
cadre_navigation = ((36.0434624891455, -78.75562797102944), (58, 7))

"GOLF DE GASCOGNE"
# position_initiale, position_finale = ((-10.018450777748733, 43.112952332964944), (-9.94154647992725, 43.337103206420466))
# bg = (42.98, -9.7)
# hd = (48.96213161620683, -0.6910580848290512)

"MEDITERRANNEE"
# position_initiale, position_finale = ((4.449957059919272, 43.03482228137273), (7.750689156750921, 39.763423641448114))
# bg = (38.07650729398917, -0.8543382853154504)
# hd = (43.585020563003646, 9.390756905813463)

"BAIE DE QUIBERON"
# position_initiale, position_finale = ((4.449957059919272, 43.03482228137273), (7.750689156750921, 39.763423641448114))
# bg = (47.464918641190074, -3.1748298590739505)
# hd = (47.58439367338987, -2.8881081611490313)

cadre_navigation = (bg, hd)
loc_nav = [bg[1], hd[1], bg[0], hd[0]]

pas_temporel = 5
pas_angle = 15
tolerance_arrivée = 1

enregistrement = False
live = True

drapeau = True

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
alpha = 0.1
tolerance = 0.01

skip = 4 

land_contact = False 