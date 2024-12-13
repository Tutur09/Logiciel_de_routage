"PARAMETRES DE NAVIGATION"

"TRAVERSEE ATLANTIQUE"
# position_finale, position_initiale = ((-3.7459774441825315, 45.608997661941785), (-60.31512438218373, 39.21922058302923))
# bg = (35.0434624891455, -72)
# hd = (63, 0)

"GOLF DE GASCOGNE"
position_finale, position_initiale = ((-9.053755416892372, 43.59017794588536), (-1.7950013543252714, 46.47621023372324))
bg = (42.98, -9.7)
hd = (48.96213161620683, -0.6910580848290512)

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



pas_temporel = 0.5
pas_angle = 5
heure_debut = 13
tolerance = 0.01
rayon_elemination = 0.05
skip = 2
land_contact = False 
tolerance_arrivée = 0.5

enregistrement = False
live = True
print = True


drapeau = True

# FICHIER METEO, TERRE
land = r'Logiciel\Carte_frontières_terrestre\ne_10m_land.shp'
vent = r'Logiciel\Données_vent\METEOCONSULT18Z_VENT_1206_Gascogne_TEMPETE.grb'
excel_wind = r'Logiciel\Données_vent\Vent.xlsx'

type = 'grib'

# Lieu enregistrement image à enregistrer
output_dir = r'C:\Users\arthu\OneDrive\Arthur\Programmation\TIPE_Arthur_Lhoste\images_png'

# PARAMETRES POUR LA POLAIRE
delimeter = r';'  # r'\s+' si Sunfastpol sinon r';'  pour Imoca 
polaire = r'Logiciel\Imoca2.pol'


"PARAMETRES VISUELS"

wind_speed_bins = [0, 2, 6, 10, 14, 17, 21, 25, 29, 33, 37, 41, 44, 47, 52, 56, 60]
colors_windy = [
    "#6271B7", "#39619F", "#4A94A9", "#4D8D7B", "#53A553", "#359F35",
    "#A79D51", "#9F7F3A", "#A16C5C", "#813A4E", "#AF5088", "#754A93",
    "#6D61A3", "#44698D", "#5C9098", "#5C9098"
]
colors_météo_marine = [
    "#A7FF91", "#A7FF91", "#75FF52", "#C1FF24", "#FBFD00", "#FEAB00",
    "#FF7100", "#FD5400", "#F80800", "#813A4E", "#AF5088", "#754A93",
    "#6D61A3", "#44698D", "#5C9098", "#5C9098"
]

# Fonctions pour activer/désactiver les prints
import sys
import os
def disable_prints():
    sys.stdout = open(os.devnull, 'w')

def enable_prints():
    sys.stdout = sys.__stdout__
    
