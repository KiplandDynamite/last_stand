import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1024, 768
MAP_WIDTH, MAP_HEIGHT = 2000, 1500  # Expanded game space
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BROWN = (139, 69, 19)
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_SPEED = 2
PLAYER_HEALTH = 3
SCORE = 0

# Set up screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Last Stand")
clock = pygame.time.Clock()

# Camera
camera_x, camera_y = 0, 0
# Player setup
player_size = 40
player = pygame.Rect(MAP_WIDTH // 2, MAP_HEIGHT // 2, player_size, player_size)
player_health = PLAYER_HEALTH

# Bullets & Enemies
bullets = []
enemies = []

# Obstacles
obstacles = [pygame.Rect(600, 600, 100, 100), pygame.Rect(1000, 800, 120, 150), pygame.Rect(300, 900, 200, 50),
             pygame.Rect(700, 300, 150, 100), pygame.Rect(1200, 500, 80, 130), pygame.Rect(500, 200, 120, 120),
             pygame.Rect(1300, 700, 100, 150)]

# Timer
start_time = pygame.time.get_ticks()

# Font for displaying score and time
font = pygame.font.Font(None, 36)

# Game loop
running = True
while running:
    screen.fill((30, 30, 30))  # Background color
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000  # Time survived in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button to shoot
                mouse_x, mouse_y = pygame.mouse.get_pos()
                bullet_dx = mouse_x + camera_x - player.centerx
                bullet_dy = mouse_y + camera_y - player.centery
                angle = math.atan2(bullet_dy, bullet_dx)
                bullet_speed_x = BULLET_SPEED * math.cos(angle)
                bullet_speed_y = BULLET_SPEED * math.sin(angle)
                bullet = pygame.Rect(player.centerx, player.centery, 10, 10)
                bullets.append([bullet, bullet_speed_x, bullet_speed_y])

    # Player movement
    new_x, new_y = player.x, player.y
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player.x > 0:
        new_x -= PLAYER_SPEED
    if keys[pygame.K_d] and player.x < MAP_WIDTH - player.width:
        new_x += PLAYER_SPEED
    if keys[pygame.K_w] and player.y > 0:
        new_y -= PLAYER_SPEED
    if keys[pygame.K_s] and player.y < MAP_HEIGHT - player.height:
        new_y += PLAYER_SPEED

    # Collision detection for player
    temp_rect = pygame.Rect(new_x, new_y, player.width, player.height)
    if not any(temp_rect.colliderect(obstacle) for obstacle in obstacles):
        player.x, player.y = new_x, new_y

    # Camera follows player
    camera_x = max(0, min(player.x - WIDTH // 2, MAP_WIDTH - WIDTH))
    camera_y = max(0, min(player.y - HEIGHT // 2, MAP_HEIGHT - HEIGHT))

    # Enemy spawning
    if random.randint(1, 30) == 1:
        spawn_side = random.choice(["TOP", "BOTTOM", "LEFT", "RIGHT"])
        if spawn_side == "TOP":
            enemy = pygame.Rect(random.randint(0, MAP_WIDTH - 40), 0, 40, 40)
        elif spawn_side == "BOTTOM":
            enemy = pygame.Rect(random.randint(0, MAP_WIDTH - 40), MAP_HEIGHT - 40, 40, 40)
        elif spawn_side == "LEFT":
            enemy = pygame.Rect(0, random.randint(0, MAP_HEIGHT - 40), 40, 40)
        else:
            enemy = pygame.Rect(MAP_WIDTH - 40, random.randint(0, MAP_HEIGHT - 40), 40, 40)
        enemies.append(enemy)

    # Enemy movement with obstacle avoidance
    for enemy in enemies[:]:
        dx, dy = player.centerx - enemy.centerx, player.centery - enemy.centery
        angle = math.atan2(dy, dx)
        new_enemy_x = enemy.x + ENEMY_SPEED * math.cos(angle)
        new_enemy_y = enemy.y + ENEMY_SPEED * math.sin(angle)
        temp_enemy_rect = pygame.Rect(new_enemy_x, new_enemy_y, enemy.width, enemy.height)

        if any(temp_enemy_rect.colliderect(obstacle) for obstacle in obstacles):
            possible_moves = [(ENEMY_SPEED, 0), (-ENEMY_SPEED, 0), (0, ENEMY_SPEED), (0, -ENEMY_SPEED)]
            valid_moves = [(move_x, move_y) for move_x, move_y in possible_moves
                           if
                           not pygame.Rect(enemy.x + move_x, enemy.y + move_y, enemy.width, enemy.height).collidelist(
                               obstacles) != -1]
            if valid_moves:
                new_enemy_x, new_enemy_y = enemy.x + valid_moves[0][0], enemy.y + valid_moves[0][1]

        enemy.x, enemy.y = new_enemy_x, new_enemy_y

        # Check for collision with player
        if enemy.colliderect(player):
            player_health -= 1
            enemies.remove(enemy)
            if player_health <= 0:
                print(f"Game Over! Time Survived: {elapsed_time} seconds. Score: {SCORE}")
                running = False

    # Bullet movement and collision detection
    for bullet in bullets[:]:
        bullet[0].x += bullet[1]
        bullet[0].y += bullet[2]

        # Check collision with obstacles
        if any(bullet[0].colliderect(obstacle) for obstacle in obstacles):
            bullets.remove(bullet)
            continue

        # Check collision with enemies
        for enemy in enemies[:]:
            if bullet[0].colliderect(enemy):
                enemies.remove(enemy)
                bullets.remove(bullet)
                SCORE += 50
                break

        # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, WHITE,
                         (bullet[0].x - camera_x, bullet[0].y - camera_y, bullet[0].width, bullet[0].height))

    # Draw everything relative to camera
    pygame.draw.rect(screen, GREEN, (player.x - camera_x, player.y - camera_y, player.width, player.height))
    for enemy in enemies:
        pygame.draw.rect(screen, RED, (enemy.x - camera_x, enemy.y - camera_y, enemy.width, enemy.height))
    for obstacle in obstacles:
        pygame.draw.rect(screen, BROWN, (obstacle.x - camera_x, obstacle.y - camera_y, obstacle.width, obstacle.height))

    # Display time survived and score
    time_text = font.render(f"Time: {elapsed_time}s", True, WHITE)
    screen.blit(time_text, (10, 10))
    score_text = font.render(f"Score: {SCORE}", True, WHITE)
    screen.blit(score_text, (WIDTH - 150, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
