#PARAMETRES LOGICIEL_CONTROLE
position_initiale, position_finale = ((-3.0620315398886806, 47.02309833024118), (-7.679471243042671, 45.13877551020408))

bg = (43.27750727162645, -9.84229985332882)
hd = (48.73899721806831, -0.25559581307713825)
loc_nav = [bg[1], hd[1], bg[0], hd[0]]

pas_temporel = 1
pas_angle = 10
tolerance_arrivée = 0.3

enregistrement = False
live = True

# PARAMETRES ROUTAGE_VENT
land = r'Logiciel\Carte_frontières_terrestre\ne_10m_land.shp'
vent = r'Logiciel\Données_vent\METEOCONSULT00Z_VENT_1110_Gascogne_départ_vendée.grb'
excel_wind = r'Logiciel\Données_vent\Vent.xlsx'


output_dir = r'C:\Users\arthu\OneDrive\Arthur\Programmation\TIPE_Arthur_Lhoste\images_png'

# PARAMETRES LOGICIEL_ROUTAGE
delimeter = r';'  # r'\s+' si Sunfastpol sinon r';'  pour Imoca 
polaire = r'Logiciel\Imoca2.pol'

heure_debut = 0
alpha = 5
tolerance = 0.01

land_contact = False 


source_vent = 'grib'