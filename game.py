import pygame
import random
import sys
from player import Player
from enemy import Enemy, FastEnemy, TankEnemy  # Import all enemy types
from obstacle import generate_town_layout
from leaderboard import save_leaderboard

# Constants
WIDTH, HEIGHT = 1024, 768
MAP_WIDTH, MAP_HEIGHT = 2400, 1800
WHITE = (255, 255, 255)
FONT = pygame.font.Font(None, 36)

WAVE_DURATION = 30000  # 30 seconds per wave
DOWN_TIME = 5000  # 5 seconds between waves
INITIAL_SPAWN_INTERVAL = 2000  # Enemies start spawning every 2 seconds


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.start_time = pygame.time.get_ticks()
        self.wave_start_time = self.start_time
        self.wave = 1
        self.score = 0
        self.last_enemy_spawn_time = pygame.time.get_ticks()
        self.spawn_interval = INITIAL_SPAWN_INTERVAL
        self.enemy_types = [Enemy]  # Start with only basic enemies

        # Create player
        self.player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2, MAP_WIDTH, MAP_HEIGHT)

        # Generate structured town layout
        self.obstacles = generate_town_layout(self.player.rect.x, self.player.rect.y)

        # Enemy list
        self.enemies = []

    def spawn_enemy(self):
        """Spawns enemies with the correct HP values and ensures weights match available enemy types."""

        # Dynamically set enemy weights to match available enemy types
        enemy_weights = [3]  # Start with normal enemies being most common

        if FastEnemy in self.enemy_types:
            enemy_weights.append(2)  # Fast enemies become available at Wave 5
        if TankEnemy in self.enemy_types:
            enemy_weights.append(1)  # Tank enemies become available at Wave 10

        # Ensure weights match the number of enemy types
        if len(enemy_weights) != len(self.enemy_types):
            raise ValueError("Enemy weights do not match the available enemy types!")

        # Pick an enemy type with correct weights
        enemy_class = random.choices(self.enemy_types, weights=enemy_weights, k=1)[0]

        x, y = random.choice([
            (random.randint(0, MAP_WIDTH), 0),  # Top edge
            (random.randint(0, MAP_WIDTH), MAP_HEIGHT),  # Bottom edge
            (0, random.randint(0, MAP_HEIGHT)),  # Left edge
            (MAP_WIDTH, random.randint(0, MAP_HEIGHT))  # Right edge
        ])

        # Manually assign HP values to each enemy type
        if enemy_class == Enemy:
            new_enemy = Enemy(x, y, 2)  # Red Guy (Normal) has 2 HP
        elif enemy_class == FastEnemy:
            new_enemy = FastEnemy(x, y)  # Yellow Guy (Fast) has 1 HP
        elif enemy_class == TankEnemy:
            new_enemy = TankEnemy(x, y)  # Blue Guy (Tank) has 5 HP

        self.enemies.append(new_enemy)  # Ensure instance is added

    def new_wave(self):
        """Increases difficulty each wave, slowing the spawn acceleration over time."""
        self.wave += 1
        self.wave_start_time = pygame.time.get_ticks()

        # Reduce the difficulty increase rate every 5 waves
        difficulty_modifier = max(0.5, 1 - (self.wave // 5) * 0.05)  # Slower reduction
        self.spawn_interval = max(500, int(INITIAL_SPAWN_INTERVAL * difficulty_modifier))

        print(f"Starting Wave {self.wave}! Spawn rate: {self.spawn_interval}ms")

        # Introduce new enemy types at wave milestones
        if self.wave == 5 and FastEnemy not in self.enemy_types:
            self.enemy_types.append(FastEnemy)
            print("Fast enemies introduced!")
        elif self.wave == 10 and TankEnemy not in self.enemy_types:
            self.enemy_types.append(TankEnemy)
            print("Tank enemies introduced!")

    def run(self):
        """Main game loop."""
        while self.running:
            self.screen.fill((30, 30, 30))
            current_time = pygame.time.get_ticks()
            elapsed_wave_time = current_time - self.wave_start_time

            # Camera follows player
            camera_x = self.player.rect.centerx - WIDTH // 2
            camera_y = self.player.rect.centery - HEIGHT // 2

            # Draw border around the map
            border_thickness = 10  # Thickness of the border lines
            border_color = (200, 200, 200)  # Light gray

            pygame.draw.rect(self.screen, border_color,
                             pygame.Rect(-camera_x, -camera_y, MAP_WIDTH, border_thickness))  # Top
            pygame.draw.rect(self.screen, border_color,
                             pygame.Rect(-camera_x, MAP_HEIGHT - camera_y - border_thickness, MAP_WIDTH,
                                         border_thickness))  # Bottom
            pygame.draw.rect(self.screen, border_color,
                             pygame.Rect(-camera_x, -camera_y, border_thickness, MAP_HEIGHT))  # Left
            pygame.draw.rect(self.screen, border_color,
                             pygame.Rect(MAP_WIDTH - camera_x - border_thickness, -camera_y, border_thickness,
                                         MAP_HEIGHT))  # Right

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click to shoot
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        self.player.shoot(mouse_x + camera_x, mouse_y + camera_y)

            # Wave system
            if elapsed_wave_time >= WAVE_DURATION:
                self.new_wave()

            # Enemy spawning
            if current_time - self.last_enemy_spawn_time > self.spawn_interval:
                self.spawn_enemy()
                self.last_enemy_spawn_time = current_time

            # Update player movement
            self.player.update(self.obstacles)

            # Update enemy movement
            for enemy in self.enemies[:]:
                enemy.update(self.player, self.obstacles)

            # Update and handle bullets
            bullets_to_remove = []
            for bullet in self.player.bullets[:]:
                bullet.update(self.obstacles, self.enemies, self)

                if bullet not in self.player.bullets:
                    continue  # Bullet already removed

                # Check for bullet collision with obstacles
                if any(obstacle.collides(bullet.rect) for obstacle in self.obstacles):
                    bullets_to_remove.append(bullet)

                # Check for bullet collision with enemies
                for enemy in self.enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        enemy_died = enemy.take_damage()  # Reduce HP

                        if enemy_died:  # Only remove if HP is zero
                            print(f"Enemy at {enemy.rect.topleft} died!")  # Debugging
                            self.enemies.remove(enemy)

                        self.score += 50
                        self.player.bullets.remove(bullet)
                        break  # Stop checking after one hit

            # Remove bullets after iteration to prevent modifying the list while looping
            for bullet in bullets_to_remove:
                if bullet in self.player.bullets:
                    self.player.bullets.remove(bullet)

            # Remove dead enemies stuck in obstacles
            for enemy in self.enemies[:]:
                if any(obstacle.collides(enemy.rect) for obstacle in self.obstacles):
                    self.enemies.remove(enemy)

            # Check if player collides with enemies (take damage)
            for enemy in self.enemies[:]:
                if enemy.rect.colliderect(self.player.rect):
                    self.player.take_damage()
                    self.enemies.remove(enemy)

            # Check if player dies
            if self.player.health <= 0:
                self.end_game()

            # Draw everything with camera offset
            self.player.draw(self.screen, camera_x, camera_y)
            for bullet in self.player.bullets:
                bullet.draw(self.screen, camera_x, camera_y)
            for enemy in self.enemies:
                enemy.draw(self.screen, camera_x, camera_y)
            for obstacle in self.obstacles:
                obstacle.draw(self.screen, camera_x, camera_y)

            # Draw UI (Wave, Score, and Player Health)
            wave_text = FONT.render(f"Wave: {self.wave}", True, WHITE)
            score_text = FONT.render(f"Score: {self.score}", True, WHITE)
            health_text = FONT.render(f"Health: {self.player.health}", True, WHITE)

            self.screen.blit(wave_text, (10, 10))
            self.screen.blit(score_text, (WIDTH - 150, 10))
            self.screen.blit(health_text, (10, HEIGHT - 50))  # Bottom-left corner

            pygame.display.flip()
            self.clock.tick(60)

    def end_game(self):
        """Ends the game and prompts for leaderboard entry."""
        name = ""
        input_active = True
        while input_active:
            self.screen.fill((30, 30, 30))
            prompt = FONT.render("Enter Your Name:", True, WHITE)
            self.screen.blit(prompt, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
            name_text = FONT.render(name, True, WHITE)
            self.screen.blit(name_text, (WIDTH // 2 - 100, HEIGHT // 2))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name:
                        save_leaderboard(name, self.score, self.wave)
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode

        from main import show_leaderboard
        show_leaderboard()
