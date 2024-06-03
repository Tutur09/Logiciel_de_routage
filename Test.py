import matplotlib.pyplot as plt

# Coordonnées des points
x = [1, 2, 3, 4, 5]
y = [2, 3, 5, 7, 11]

# Création du graphique
plt.plot(x, y, marker='o')  # 'o' est le style du marqueur pour afficher les points

# Ajout de titres et étiquettes
plt.title('Relier des Points avec Matplotlib')
plt.xlabel('Axe des x')
plt.ylabel('Axe des y')

# Affichage du graphique
plt.show()
