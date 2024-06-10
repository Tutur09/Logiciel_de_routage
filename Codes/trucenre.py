import pygame
import math

# Initialisation de Pygame
pygame.init()

# Paramètres de la fenêtre
width, height = 800, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Simulation de Physique')

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Paramètres de la boule
ball_radius = 15
ball_pos = [width // 2, height // 2]
ball_vel = [0, 0]
ball_acc = [0, 0.5]  # Gravité

# Paramètres de la droite
line_start = (100, 500)
line_end = (700, 500)

# Fonction pour vérifier la collision avec la droite
def check_collision(ball_pos, ball_vel, line_start, line_end):
    # Equation de la droite y = mx + b
    dx = line_end[0] - line_start[0]
    dy = line_end[1] - line_start[1]
    if dx == 0:
        return False  # Evite la division par zéro
    m = dy / dx
    b = line_start[1] - m * line_start[0]

    # Position de la boule au prochain frame
    next_x = ball_pos[0] + ball_vel[0]
    next_y = ball_pos[1] + ball_vel[1]

    # Vérifie si la boule est en dessous de la droite
    line_y_at_ball = m * next_x + b

    # Collision détectée
    if next_y + ball_radius >= line_y_at_ball and line_start[0] <= next_x <= line_end[0]:
        return True
    return False

# Fonction pour gérer la réponse à la collision
def handle_collision(ball_vel):
    ball_vel[1] = -ball_vel[1] * 0.7  # Inverse la vitesse y et applique un facteur de rebond

# Boucle principale
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Mise à jour de la position de la boule
    ball_vel[0] += ball_acc[0]
    ball_vel[1] += ball_acc[1]
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Vérifie la collision et gère la réponse
    if check_collision(ball_pos, ball_vel, line_start, line_end):
        handle_collision(ball_vel)

    # Empêche la boule de sortir de l'écran (rebond aux bords de la fenêtre)
    if ball_pos[0] <= ball_radius or ball_pos[0] >= width - ball_radius:
        ball_vel[0] = -ball_vel[0]
    if ball_pos[1] <= ball_radius or ball_pos[1] >= height - ball_radius:
        ball_vel[1] = -ball_vel[1]

    # Dessin de la scène
    window.fill(BLACK)
    pygame.draw.line(window, WHITE, line_start, line_end, 2)
    pygame.draw.circle(window, WHITE, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
