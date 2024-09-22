import Logicielroutage_en_dev as lr
import Routage_Vent_en_dev as rv

# Exemple d'utilisation
position_initiale = (-3.067, 47.58)
position_finale = (-1.667, 43.59)

pas_temporel = 3
pas_angle = 15

#Chemin d'accès du fichier GRIB    
file_path = 'C:/Users/arthu/OneDrive/Arthur/Programmation/TIPE_Arthur_Lhoste/Logiciel/Données_vent/METEOCONSULT12Z_VENT_0921_Gascogne.grb'
file_path_courant = 'C:/Users/arthu/OneDrive/Arthur/Programmation/TIPE_Arthur_Lhoste/Logiciel/Données_vent/METEOCONSULT00Z_COURANT_0921_Gascogne.grb'

lr.itere_jusqua_dans_enveloppe(position_initiale, position_finale, pas_temporel, pas_angle, 0.5, live = False, enregistrement = False)