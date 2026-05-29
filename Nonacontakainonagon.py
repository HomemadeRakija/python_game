import pygame
import sys
import math

pygame.init()

# Screen
WIDTH, HEIGHT = 1080, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Square")
clock = pygame.time.Clock()

# Colors
WHITE = (240, 240, 240)
BLUE = (0, 150, 255)
DARK = (30, 30, 30)

# Square (player)
size = 40
x = WIDTH // 2 - size // 2
y = HEIGHT - size - 50

player_pos = pygame.Vector2(x, 0)
player_vel = pygame.Vector2(0, 0)
predicted_vel = pygame.Vector2(0,0)
gravity = 0.6
on_ground = False
dragging = False
launch_power = 0.2
MAX_VELOCITY = 5
friction = 1.05

# Ground
ground_y = HEIGHT - 50


# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            dragging = True
            player_vel = pygame.Vector2(0,0)
        elif event.type == pygame.MOUSEBUTTONUP:
           if dragging:
            dragging = False
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            direction = player_pos - mouse_pos
            max_lenght = 150
            if direction.length() > max_lenght:
               direction.scale_to_length (max_lenght)
            player_vel = direction * launch_power
            predicted_vel = direction * launch_power


    
    # Apply gravity
    if not dragging:
        player_vel.y += gravity
        player_pos+= player_vel
    

    # Collision with ground
    if player_pos[1]+ size >= ground_y:
            player_pos[1] = ground_y - size
            on_ground = True
            #friskjon
            player_vel = player_vel / friction



    # Draw
    screen.fill(DARK)

    # Ground
    pygame.draw.rect(screen, WHITE, (0, ground_y, WIDTH, HEIGHT - ground_y))

    # Square
    pygame.draw.rect(screen, BLUE, (player_pos.x,player_pos.y, size, size))

    #kalkulert turte av spilleren
    for i in range(60):
        predicted_vel.y += gravity
        predicted_pos = player_pos.copy()

    pygame.draw.circle(screen, WHITE, (int(predicted_pos.x + size / 2), int(predicted_pos.y + size / 2)), 4)

    pygame.display.flip()
    clock.tick(60)
