import pygame
import sys
import random
import time

pygame.init()

# ---------------------- Constants ----------------------
WIDTH, HEIGHT = 800, 600
WORLD_WIDTH, WORLD_HEIGHT = 3000, 2000

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slingshot Movement - Purple Ball Target")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# ---------------------- Player ----------------------
player_pos = pygame.Vector2(400, 300)
player_vel = pygame.Vector2(0, 0)
radius = 20
gravity = pygame.Vector2(0, 0.6)
dragging = False
launch_power = 0.4

# ---------------------- Camera ----------------------
camera = pygame.Vector2(0, 0)
wall_thickness = 40

# ---------------------- Game Objects ----------------------
targets = []
target_radius = 10
max_targets = 30
score = 0

spiky_balls = []
spiky_radius = 15
spiky_spawn_chance = 0.05
spiky_respawn_time = 30

purple_balls = []  # Can have multiple
purple_radius = 50
purple_spawn_chance = 0.05
purple_health = 2
projectile_interval = 3.5  # seconds
projectile_speed = 3.5  # projectile speed

projectiles = []
particles = []

time_scale = 1
projectile_lifetime = 5  # seconds until projectile explodes

# ---------------------- Functions ----------------------
def spawn_target():
    while True:
        x = random.randint(wall_thickness + target_radius, WORLD_WIDTH - wall_thickness - target_radius)
        y = random.randint(wall_thickness + target_radius, WORLD_HEIGHT - wall_thickness - target_radius)
        if pygame.Vector2(x, y).distance_to(player_pos) > 200:
            roll = random.random()
            if roll < spiky_spawn_chance:
                spiky_balls.append({"pos": pygame.Vector2(x, y), "spawn_time": time.time()})
            elif roll < spiky_spawn_chance + purple_spawn_chance:
                purple_balls.append({"pos": pygame.Vector2(x, y), "last_shot": time.time(), "health": purple_health})
            else:
                targets.append(pygame.Vector2(x, y))
            break

def respawn_spiky_balls():
    now = time.time()
    for ball in spiky_balls:
        if now - ball["spawn_time"] >= spiky_respawn_time:
            while True:
                x = random.randint(wall_thickness + spiky_radius, WORLD_WIDTH - wall_thickness - spiky_radius)
                y = random.randint(wall_thickness + spiky_radius, WORLD_HEIGHT - wall_thickness - spiky_radius)
                if pygame.Vector2(x, y).distance_to(player_pos) > 200:
                    ball["pos"] = pygame.Vector2(x, y)
                    ball["spawn_time"] = now
                    break

def draw_trajectory(start_pos, start_vel):
    sim_pos = start_pos.copy()
    sim_vel = start_vel.copy()
    for _ in range(60):
        sim_vel += gravity
        sim_pos += sim_vel
        # Wall collisions
        if sim_pos.y > WORLD_HEIGHT - wall_thickness - radius:
            sim_pos.y = WORLD_HEIGHT - wall_thickness - radius
            sim_vel.y *= -0.6
            sim_vel.x *= 0.8
        if sim_pos.y < wall_thickness + radius:
            sim_pos.y = wall_thickness + radius
            sim_vel.y *= -0.6
        if sim_pos.x < wall_thickness + radius:
            sim_pos.x = wall_thickness + radius
            sim_vel.x *= -0.6
        if sim_pos.x > WORLD_WIDTH - wall_thickness - radius:
            sim_pos.x = WORLD_WIDTH - wall_thickness - radius
            sim_vel.x *= -0.6
        pygame.draw.circle(screen, (180, 180, 180), sim_pos - camera, 3)

def shoot_projectile(purple):
    direction = (player_pos - purple["pos"]).normalize()
    projectiles.append({"pos": purple["pos"].copy(), "vel": direction * projectile_speed, "spawn_time": time.time()})

def explode(pos):
    for _ in range(15):
        angle = random.uniform(0,360)
        speed = random.uniform(2,5)
        vel = pygame.Vector2(1,0).rotate(angle) * speed
        particles.append([pos.copy(), vel, 30])

def reset_game():
    global player_pos, player_vel, targets, spiky_balls, purple_balls, projectiles, particles, score
    player_pos = pygame.Vector2(400, 300)
    player_vel = pygame.Vector2(0,0)
    targets.clear()
    spiky_balls.clear()
    purple_balls.clear()
    projectiles.clear()
    particles.clear()
    score = 0

# ---------------------- Main Game Loop ----------------------
while True:
    dt = clock.tick(60) / 16.67
    died = False  # Initialize died at start

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                dragging = False
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                world_mouse = mouse_pos + camera
                direction = player_pos - world_mouse
                max_length = 150
                if direction.length() > max_length:
                    direction.scale_to_length(max_length)
                player_vel = direction * launch_power

    # Slow motion
    time_scale = 0.3 if dragging else 1

    # Spawn / Respawn
    while len(targets) + len(spiky_balls) + len(purple_balls) < max_targets:
        spawn_target()
    respawn_spiky_balls()

    # Player physics
    if not dragging:
        player_vel += gravity * dt * time_scale
        player_pos += player_vel * dt * time_scale
    else:
        player_vel = pygame.Vector2(0,0)

    # Wall collisions
    if player_pos.y > WORLD_HEIGHT - wall_thickness - radius:
        player_pos.y = WORLD_HEIGHT - wall_thickness - radius
        player_vel.y *= -0.6
        player_vel.x *= 0.8
    if player_pos.y < wall_thickness + radius:
        player_pos.y = wall_thickness + radius
        player_vel.y *= -0.6
    if player_pos.x < wall_thickness + radius:
        player_pos.x = wall_thickness + radius
        player_vel.x *= -0.6
    if player_pos.x > WORLD_WIDTH - wall_thickness - radius:
        player_pos.x = WORLD_WIDTH - wall_thickness - radius
        player_vel.x *= -0.6

    # Target collisions
    for target in targets[:]:
        offset = player_pos - target
        distance = offset.length()
        if distance < radius + target_radius:
            if distance == 0:
                offset = pygame.Vector2(1,0)
                distance = 1
            normal = offset.normalize()
            overlap = radius + target_radius - distance
            player_pos += normal * overlap
            player_vel = player_vel.reflect(normal) * 0.9
            for _ in range(8):
                angle = random.uniform(0,360)
                speed = random.uniform(2,6)
                vel = pygame.Vector2(1,0).rotate(angle) * speed
                particles.append([target.copy(), vel, 30])
            targets.remove(target)
            score += 100

    # Spiky ball collisions
    for ball in spiky_balls:
        if player_pos.distance_to(ball["pos"]) < radius + spiky_radius:
            died = True

    # Purple balls behavior (stationary)
    now = time.time()
    for purple in purple_balls[:]:
        # Shoot projectile every 3.5 seconds, scaled by time_scale
        if now - purple["last_shot"] > projectile_interval / time_scale:
            shoot_projectile(purple)
            purple["last_shot"] = now

    # Update projectiles
    for proj in projectiles[:]:
        if now - proj["spawn_time"] >= projectile_lifetime:
            explode(proj["pos"])
            projectiles.remove(proj)
            continue
        dir_to_player = (player_pos - proj["pos"]).normalize()
        proj["vel"] = dir_to_player * projectile_speed
        proj["pos"] += proj["vel"] * dt * time_scale
        if player_pos.distance_to(proj["pos"]) < radius:
            died = True

    # Player can hit purple balls
    for purple in purple_balls[:]:
        offset = player_pos - purple["pos"]
        distance = offset.length()
        if distance < radius + purple_radius:
            purple["health"] -= 1
            if purple["health"] <= 0:
                explode(purple["pos"])
                purple_balls.remove(purple)
                score += 500  # <-- Give 500 points instead of 300
            # Bounce player slightly
            player_vel = player_vel.reflect(offset.normalize()) * 0.8

    # Reset on death
    if died:
        reset_game()
        continue

    # Camera
    target_cam = player_pos - pygame.Vector2(WIDTH//2, HEIGHT//2)
    camera += (target_cam - camera) * 0.1
    camera.x = max(0, min(camera.x, WORLD_WIDTH - WIDTH))
    camera.y = max(0, min(camera.y, WORLD_HEIGHT - HEIGHT))

    # ---------------------- Draw ----------------------
    screen.fill((30,30,30))
    if dragging:
        overlay = pygame.Surface((WIDTH,HEIGHT))
        overlay.set_alpha(80)
        overlay.fill((0,0,0))
        screen.blit(overlay,(0,0))

    # Walls
    walls = [
        pygame.Rect(0,0,WORLD_WIDTH,wall_thickness),
        pygame.Rect(0,WORLD_HEIGHT-wall_thickness,WORLD_WIDTH,wall_thickness),
        pygame.Rect(0,0,wall_thickness,WORLD_HEIGHT),
        pygame.Rect(WORLD_WIDTH-wall_thickness,0,wall_thickness,WORLD_HEIGHT)
    ]
    for wall in walls:
        pygame.draw.rect(screen,(120,120,120), wall.move(-camera.x,-camera.y))

    # Targets
    for target in targets:
        pygame.draw.circle(screen,(255,60,60), target - camera, target_radius)

    # Spiky balls
    for ball in spiky_balls:
        pos = ball["pos"]
        pygame.draw.circle(screen,(0,255,0), pos - camera, spiky_radius)
        for angle in range(0,360,45):
            end = pos + pygame.Vector2(spiky_radius+5,0).rotate(angle)
            pygame.draw.line(screen,(0,200,0), pos - camera, end - camera, 2)

    # Purple balls
    for purple in purple_balls:
        pygame.draw.circle(screen,(150,0,200), purple["pos"] - camera, purple_radius)
        # Draw HP bar INSIDE the purple ball
        hp_ratio = purple["health"] / purple_health
        bar_width = purple_radius * 1.5
        bar_height = 8
        bar_x = purple["pos"].x - bar_width / 2 - camera.x
        bar_y = purple["pos"].y - bar_height / 2 - camera.y
        pygame.draw.rect(screen, (50,50,50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0,255,0), (bar_x, bar_y, bar_width * hp_ratio, bar_height))

    # Projectiles
    for proj in projectiles:
        pygame.draw.circle(screen,(200,0,200), proj["pos"] - camera, 10)

    # Trajectory
    if dragging:
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        world_mouse = mouse_pos + camera
        direction = player_pos - world_mouse
        max_length = 150
        if direction.length() > max_length:
            direction.scale_to_length(max_length)
        preview_vel = direction * launch_power
        draw_trajectory(player_pos, preview_vel)
        pygame.draw.line(screen,(200,200,200), player_pos - camera, world_mouse - camera, 2)

    # Player
    pygame.draw.circle(screen,(50,200,255), player_pos - camera, radius)

    # Particles
    for p in particles[:]:
        p[0] += p[1] * dt * time_scale
        p[2] -= 1
        pygame.draw.circle(screen,(255,200,50), p[0]-camera,3)
        if p[2]<=0:
            particles.remove(p)

    # Score
    score_text = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(score_text,(20,20))

    pygame.display.flip()
