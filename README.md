# Logiciel de Routage Vent

## Description

Ce logiciel permet de calculer et d'analyser des itinéraires en tenant compte des données de vent. Il est conçu pour aider à l'optimisation des trajets en mer ou dans les zones affectées par des conditions de vent variables.

## Fonctionnalités

- Chargement de données de vent à partir de fichiers GRIB.
- Visualisation des itinéraires avec des vecteurs de vent en temps réel.
- Calcul d'itinéraires optimisés selon des paramètres définis par l'utilisateur.

## Nouveautés

### Ajouts récents (21 septembre 2024)

- **Visualisation de la Route Idéale** : La fonction `enregistrement_route_avec_vent` a été ajoutée, permettant de tracer la route idéale heure par heure.
- **Intégration des Vecteurs de Vent** : Chaque plot enregistré inclut les vecteurs de vent correspondant à l'heure choisie.
- **Amélioration de l'Enregistrement** : Les plots sont maintenant sauvegardés dans un répertoire spécifié, avec des noms de fichiers indiquant l'heure.

## Utilisation
Me demander et pas évident d'installer cfgrib 

![Carte de vent défini par l'utilisateur](https://github.com/Tutur09/Logiciel_de_routage/raw/main/Exemple.png)
![Récupération du vent en temps réel grâçe aux fichiers GRIB de Météo Marine](https://github.com/Tutur09/Logiciel_de_routage/raw/main/route_ideale/route_ideale_vent_heure_18.png)

