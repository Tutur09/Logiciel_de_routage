# Logiciel de Routage

## Description

Ce logiciel permet de calculer et d'analyser des itinéraires en tenant compte des données de vent. Il est conçu pour aider à l'optimisation des trajets en mer ou dans les zones affectées par des conditions de vent variables.

## Utilisation du routeur
J'ai partagé une environnement conda avec toutes les bibliothèques nécessaire au fonctionnement.
- Télécharger anaconda3
- Télécharger le document `routage_env.yml` et l'ouvrir avec conda
- Télécharger le dossier avec toutes les fonctions nécessaires (données de vent, polaires de vitesse, scripts python, ...)

## Fonctionnalités

- Chargement de données de vent à partir de fichiers GRIB.
- Visualisation des itinéraires avec des vecteurs de vent en temps réel.
- Calcul d'itinéraires optimisés selon des paramètres définis par l'utilisateur.

## Nouveautés

### Ajouts récents (21 septembre 2024)

- **Visualisation de la Route Idéale** : La fonction `enregistrement_route_avec_vent` a été ajoutée, permettant de tracer la route idéale heure par heure.
- **Intégration des Vecteurs de Vent** : Chaque plot enregistré inclut les vecteurs de vent correspondant à l'heure choisie.
- **Amélioration de l'Enregistrement** : Les plots sont maintenant sauvegardés dans un répertoire spécifié, avec des noms de fichiers indiquant l'heure.

### Novembre-décembre finalisation du logiciel pour le TIPE
- Possibilités de déterminer la route idéal avec un aperçu en direct ou visualisation a la fin de la route
- Grille de vent venant d'un grib meteo France ou carte des vents personnalisée via excel

## Utilisation
Me demander et pas évident d'installer cfgrib 

## EXEMPLES
![Carte de vent défini par l'utilisateur](https://github.com/Tutur09/Logiciel_de_routage/raw/main/Exemple.png)
_Carte de vent défini par l'utilisateur_

![Récupération du vent en temps réel grâçe aux fichiers GRIB de Météo Marine](https://github.com/Tutur09/Logiciel_de_routage/raw/main/route_ideale/route_ideale_vent_heure_18.png)
_Récupération du vent en temps réel grâçe aux fichiers GRIB de Météo Marine_

![](https://github.com/Tutur09/Logiciel_de_routage/raw/main/route_ideale/route_ideale_vent_heure_42.png)

(https://github.com/Tutur09/Logiciel_de_routage/raw/main/Carte_vents.png)