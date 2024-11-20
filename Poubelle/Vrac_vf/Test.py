import matplotlib.pyplot as plt

# Crée un simple plot
fig, ax = plt.subplots()
ax.plot([0, 1, 2, 3], [10, 20, 25, 30])

# Fonction pour gérer le clic
def on_click(event):
    if event.inaxes:  # Vérifie que le clic est dans les axes
        x, y = event.xdata, event.ydata
        print(f"Coordonnées du clic: x={x}, y={y}")

# Connexion de l'événement de clic
cid = fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()
