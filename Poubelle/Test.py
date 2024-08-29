
import pygrib

# Remplace 'path_to_your_grib_file.grib' par le chemin réel de ton fichier GRIB
grib_file = 'C:\Users\arthu\OneDrive\Arthur\Programmation\TIPE_Arthur_Lhoste\Logiciel\METEOCONSULT12Z_VENT_0829_Gascogne.grb'

try:
    grbs = pygrib.open(grib_file)
    print(f"Fichier GRIB {grib_file} ouvert avec succès!")

    # Affiche les clés des premiers messages
    for grb in grbs[:5]:
        print(grb)

except Exception as e:
    print(f"Erreur lors de l'ouverture du fichier GRIB : {e}")
