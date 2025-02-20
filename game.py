import pygame
import random
import sys
from player import Player
from enemy import Enemy, FastEnemy, TankEnemy, DasherEnemy, ShooterEnemy, SwarmEnemy  # Import all enemy types
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

# XP Bar Settings
XP_BAR_WIDTH = WIDTH // 2
XP_BAR_HEIGHT = 20
XP_BAR_X = (WIDTH - XP_BAR_WIDTH) // 2
XP_BAR_Y = 10  #

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused_for_upgrade = False  # ⬅️ Add this flag to pause the game
        self.start_time = pygame.time.get_ticks()
        self.wave_start_time = self.start_time
        self.wave = 1
        self.score = 0
        self.last_enemy_spawn_time = pygame.time.get_ticks()
        self.spawn_interval = INITIAL_SPAWN_INTERVAL
        self.enemy_types = [Enemy, FastEnemy, TankEnemy, DasherEnemy, ShooterEnemy, SwarmEnemy]  # Start with only basic enemies
        self.death_animations = []  # Store active death animations
        self.enemy_bullets = [] # Store bullets fired by shooter enemies
        self.currency_drops = [] # Store currency of player

        self.explosions = []

        # Create player
        self.player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2, MAP_WIDTH, MAP_HEIGHT)

        # Camera follows player
        self.camera_x = self.player.rect.centerx - WIDTH // 2
        self.camera_y = self.player.rect.centery - HEIGHT // 2

        # Generate structured town layout
        self.obstacles = generate_town_layout(self.player.rect.x, self.player.rect.y)

        # Enemy list
        self.enemies = []

    def spawn_enemy(self):
        """Spawns enemies dynamically, including swarm enemies in clustered formations."""
        enemy_weights = [3]  # Default: Normal enemies are common

        if FastEnemy in self.enemy_types:
            enemy_weights.append(2)  # Fast enemies available at Wave 5
        if TankEnemy in self.enemy_types:
            enemy_weights.append(1)  # Tank enemies available at Wave 10
        if DasherEnemy in self.enemy_types:
            enemy_weights.append(3)  # Dashers are moderately common
        if ShooterEnemy in self.enemy_types:
            enemy_weights.append(2)  # Shooters are moderately common
        if SwarmEnemy in self.enemy_types:
            enemy_weights.append(2)  # Swarm enemies are slightly more common

        # Ensure enemy type selection remains valid
        if len(enemy_weights) != len(self.enemy_types):
            raise ValueError("Enemy weights do not match the available enemy types!")

        enemy_class = random.choices(self.enemy_types, weights=enemy_weights, k=1)[0]

        # Randomize spawn location (from edges of the map)
        base_x, base_y = random.choice([
            (random.randint(0, MAP_WIDTH), 0),  # Top edge
            (random.randint(0, MAP_WIDTH), MAP_HEIGHT),  # Bottom edge
            (0, random.randint(0, MAP_HEIGHT)),  # Left edge
            (MAP_WIDTH, random.randint(0, MAP_HEIGHT))  # Right edge
        ])

        # Special case: If the selected enemy is SwarmEnemy, spawn a clustered group
        if enemy_class == SwarmEnemy:
            swarm_group = []  # List to store all swarm members

            for i in range(5):  # Spawn a group of 5
                offset_x = random.randint(-30, 30)  # Small offset for clustering
                offset_y = random.randint(-30, 30)

                # Ensure enemies don’t spawn inside obstacles
                spawn_rect = pygame.Rect(base_x + offset_x, base_y + offset_y, 25, 25)
                if any(obstacle.collides(spawn_rect) for obstacle in self.obstacles):
                    continue  # Skip this spawn if it collides

                swarm_member = SwarmEnemy(base_x + offset_x, base_y + offset_y, swarm_group)
                swarm_group.append(swarm_member)  # Add to the group
                self.enemies.append(swarm_member)
        else:
            # Standard enemy spawning
            if enemy_class == Enemy:
                new_enemy = Enemy(base_x, base_y, 3)  # Normal enemies
            elif enemy_class == FastEnemy:
                new_enemy = FastEnemy(base_x, base_y)  # Fast enemies
            elif enemy_class == TankEnemy:
                new_enemy = TankEnemy(base_x, base_y)  # Tank enemies
            elif enemy_class == DasherEnemy:
                new_enemy = DasherEnemy(base_x, base_y)  # Dasher enemies
            elif enemy_class == ShooterEnemy:
                new_enemy = ShooterEnemy(base_x, base_y)  # Shooter enemies

            self.enemies.append(new_enemy)

    def new_wave(self):
        """Increases difficulty each wave, slowing the spawn acceleration over time."""
        self.wave += 1
        self.wave_start_time = pygame.time.get_ticks()

        # Reduce the difficulty increase rate every 5 waves
        difficulty_modifier = max(0.5, 1 - (self.wave // 5) * 0.05)  # Slower reduction
        self.spawn_interval = max(500, int(INITIAL_SPAWN_INTERVAL * difficulty_modifier))

        print(f"Starting Wave {self.wave}! Spawn rate: {self.spawn_interval}ms")

        # Introduce new enemy types at wave milestones
        if self.wave == 3 and FastEnemy not in self.enemy_types:
            self.enemy_types.append(FastEnemy)
            print("Fast enemies introduced!")
        elif self.wave == 5 and TankEnemy not in self.enemy_types:
            self.enemy_types.append(TankEnemy)
            print("Tank enemies introduced!")
        elif self.wave == 7 and DasherEnemy not in self.enemy_types:
            self.enemy_types.append(DasherEnemy)
            print("Dashers introduced!")
        elif self.wave >= 9 and ShooterEnemy not in self.enemy_types:
            self.enemy_types.append(ShooterEnemy)
            print("Shooter enemies introduced!")
        elif self.wave >= 11 and SwarmEnemy not in self.enemy_types:
            self.enemy_types.append(SwarmEnemy)
            print("Swarm Enemies introduced!")

    def run(self):
        """Main game loop."""
        while self.running:
            self.screen.fill((30, 30, 30))
            current_time = pygame.time.get_ticks()
            elapsed_wave_time = current_time - self.wave_start_time

            self.camera_x = self.player.rect.centerx - WIDTH // 2
            self.camera_y = self.player.rect.centery - HEIGHT // 2

            # If waiting for an upgrade selection, only process input
            if self.paused_for_upgrade:
                self.handle_upgrade_input()
                self.draw_upgrade_screen()  # ✅ Fix: Now draws the upgrade UI
                self.clock.tick(60)
                continue

            current_time = pygame.time.get_ticks()
            elapsed_wave_time = current_time - self.wave_start_time

            # Draw border around the map
            border_thickness = 10  # Thickness of the border lines
            border_color = (200, 200, 200)  # Light gray

            pygame.draw.rect(self.screen, border_color,
                             pygame.Rect(-self.camera_x, -self.camera_y, MAP_WIDTH, border_thickness))  # Top
            pygame.draw.rect(self.screen, border_color,
                             pygame.Rect(- self.camera_x, MAP_HEIGHT - self.camera_y - border_thickness, MAP_WIDTH,
                                         border_thickness))  # Bottom
            pygame.draw.rect(self.screen, border_color,
                             pygame.Rect(-self.camera_x, -self.camera_y, border_thickness, MAP_HEIGHT))  # Left
            pygame.draw.rect(self.screen, border_color,
                             pygame.Rect(MAP_WIDTH - self.camera_x - border_thickness, -self.camera_y, border_thickness,
                                         MAP_HEIGHT))  # Right

            keys = pygame.key.get_pressed()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.paused_for_upgrade:
                    self.handle_upgrade_input()
                    self.draw_upgrade_screen()
                    self.clock.tick(60)
                    continue

                if self.paused_for_upgrade and event.type == pygame.KEYDOWN:
                    self.player.handle_level_up_input(event.key, self)  # Let player pick an upgrade

                if not self.paused_for_upgrade:  # Only process other inputs if game is not paused
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left click to shoot
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            self.player.shoot(mouse_x + self.camera_x, mouse_y + self.camera_y)

                    # Explosive Shot (Press Q)
                    if keys[pygame.K_q]:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        self.player.use_explosive_shot(mouse_x + self.camera_x, mouse_y + self.camera_y, self)

                    # Sword Attack (Press E)
                    if keys[pygame.K_e]:
                        self.player.use_sword_attack(self)

                    # Dash (Press Shift)
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        self.player.use_dash(self)

                # Open shop when 'B' is pressed
                if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                    self.open_shop()

            # Wave system
            if elapsed_wave_time >= WAVE_DURATION:
                self.new_wave()

            # Enemy spawning
            if current_time - self.last_enemy_spawn_time > self.spawn_interval:
                self.spawn_enemy()
                self.last_enemy_spawn_time = current_time

            # Update player movement
            self.player.update(self.obstacles, self)

            # Update enemy movement
            for enemy in self.enemies[:]:
                if isinstance(enemy, ShooterEnemy):
                    enemy.update(self.player, self.obstacles, self.enemy_bullets)  # Pass bullets list
                else:
                    enemy.update(self.player, self.obstacles, self)  # Normal enemies don't need bullets

            for bullet in self.player.bullets[:]:  # Iterate over a copy to avoid modification issues
                bullet.update(self.obstacles, self.enemies, self)

            # Update and handle bullets
            bullets_to_remove = []
            for bullet in self.player.bullets[:]:  # Iterate over a copy to safely remove bullets
                if bullet.rect is None:
                    continue  # Skip bullets that were already removed

                for enemy in self.enemies:
                    if enemy.rect is not None and bullet.rect.colliderect(enemy.rect):
                        self.player.bullets.remove(bullet)
                        bullet.hit_enemy(enemy, self)  # ✅ Hand off enemy hit logic to bullet.py
                        break  # Exit loop after bullet hits something

            # Remove bullets after iteration to prevent modifying the list while looping
            for bullet in bullets_to_remove:
                if bullet in self.player.bullets:
                    self.player.bullets.remove(bullet)

            # Remove dead enemies stuck in obstacles
            for enemy in self.enemies[:]:
                if any(obstacle.collides(enemy.rect) for obstacle in self.obstacles):
                    self.enemies.remove(enemy)

            # Update enemy bullets (ShooterBullets)
            for bullet in self.enemy_bullets[:]:  # Iterate over a copy to safely remove bullets
                bullet.update(self.player, self.obstacles, self.enemy_bullets)

            # Draw enemy bullets
            for bullet in self.enemy_bullets:
                bullet.draw(self.screen, self.camera_x, self.camera_y)

            # Check if player collides with enemies (take damage)
            for enemy in self.enemies:
                if enemy.rect is not None and enemy.rect.colliderect(self.player.rect):
                    self.player.take_damage()
                    self.enemies.remove(enemy)

            # Check if player dies
            if self.player.health <= 0:
                self.end_game()

            # Check for currency pickups
            for currency in self.currency_drops[:]:
                if currency.check_pickup(self.player):  # If collected, remove it
                    self.currency_drops.remove(currency)

            # Death animation for enemies
            for animation in self.death_animations[:]:  # Iterate over a copy for safe removal
                if animation.update():
                    self.death_animations.remove(animation)

            # Fire extra bullets
            self.player.update_bullets()

            # Draw everything with camera offset
            self.player.draw(self.screen, self.camera_x, self.camera_y)
            for bullet in self.player.bullets:
                bullet.draw(self.screen, self.camera_x, self.camera_y)
            for enemy in self.enemies:
                enemy.draw(self.screen, self.camera_x, self.camera_y)
            for obstacle in self.obstacles:
                obstacle.draw(self.screen, self.camera_x, self.camera_y)

            # Draw death animations
            for animation in self.death_animations:
                animation.draw(self.screen, self.camera_x, self.camera_y)

            # ✅ Draw explosion effects
            for explosion in self.explosions[:]:
                if explosion.draw(self.screen, self.camera_x, self.camera_y):
                    self.explosions.remove(explosion)  # Remove explosion after animation

            # Draw currency drops
            for currency in self.currency_drops:
                currency.draw(self.screen, self.camera_x, self.camera_y)

            # Draw UI (Wave, Score, and Player Health)
            wave_text = FONT.render(f"Wave: {self.wave}", True, WHITE)
            score_text = FONT.render(f"Score: {self.score}", True, WHITE)
            health_text = FONT.render(f"Health: {self.player.health}", True, WHITE)
            currency_text = FONT.render(f"Coins: {self.player.currency}", True, (192, 192, 192))  # Silver text
            text_width, text_height = currency_text.get_size()
            self.screen.blit(currency_text, (WIDTH - text_width - 20, HEIGHT - text_height - 20))

            # Calculate XP progress width
            xp_progress_width = int((self.player.xp / self.player.xp_to_next_level) * XP_BAR_WIDTH)

            # Draw XP bar background (gray)
            pygame.draw.rect(self.screen, (100, 100, 100), (XP_BAR_X, XP_BAR_Y, XP_BAR_WIDTH, XP_BAR_HEIGHT))

            # Draw XP progress (blue)
            pygame.draw.rect(self.screen, (50, 150, 255), (XP_BAR_X, XP_BAR_Y, xp_progress_width, XP_BAR_HEIGHT))

            # Draw Level (centered below the XP bar)
            level_text = FONT.render(f"Lvl: {self.player.level}", True, (255, 255, 255))
            level_text_x = XP_BAR_X + (XP_BAR_WIDTH - level_text.get_width()) // 2  # Center text
            level_text_y = XP_BAR_Y + XP_BAR_HEIGHT + 5  # ✅ Place text **below** the XP bar
            self.screen.blit(level_text, (level_text_x, level_text_y))

            self.screen.blit(wave_text, (10, 10))
            self.screen.blit(score_text, (WIDTH - 150, 10))
            self.screen.blit(health_text, (10, HEIGHT - 50))  # Bottom-left corner

            pygame.display.flip()
            self.clock.tick(60)

    def handle_upgrade_input(self):
        """Handles player input for selecting an upgrade."""
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.player.handle_level_up_input(event.key, self)

    def draw_upgrade_screen(self):
        """Displays the upgrade selection screen while keeping the game scene visible."""
        # 1️⃣ Draw the current game scene first (instead of clearing)
        self.screen.fill((30, 30, 30))  # Keep background visible

        camera_x = self.player.rect.centerx - WIDTH // 2
        camera_y = self.player.rect.centery - HEIGHT // 2

        # Draw all game elements
        for bullet in self.player.bullets:
            bullet.draw(self.screen, self.camera_x, self.camera_y)
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x, self.camera_y)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen, self.camera_x, self.camera_y)
        self.player.draw(self.screen, self.camera_x, self.camera_y)

        # 2️⃣ Overlay a semi-transparent dark box to highlight the menu
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark transparent overlay
        self.screen.blit(overlay, (0, 0))

        # 3️⃣ Draw Level-Up UI on top
        title_text = FONT.render("LEVEL UP! Choose an Upgrade:", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)

        if self.player.pending_ability_choices:
            for i, ability in enumerate(self.player.pending_ability_choices, 1):  # ✅ Add a loop
                text = FONT.render(f"{i}: {ability['name']} - {ability['description']}", True, WHITE)
                text_rect = text.get_rect(center=(WIDTH // 2, 200 + i * 50))
                self.screen.blit(text, text_rect)

        pygame.display.flip()  # ✅ Now updates the screen without removing the game state

    def open_shop(self):
        """Pauses the game and displays the shop UI."""
        shop_open = True

        while shop_open:
            self.screen.fill((30, 30, 30))  # Dark background
            title = FONT.render("Shop - Press ESC to Exit", True, (255, 255, 255))
            self.screen.blit(title, (WIDTH // 2 - 100, 50))

            # Define available utility abilities
            upgrades = [
                {"name": "Explosive Shot", "cost": 30, "effect": self.player.unlock_explosive_shot},
                {"name": "Sword Attack", "cost": 25, "effect": self.player.unlock_sword_attack},
                {"name": "Dash Ability", "cost": 20, "effect": self.player.unlock_dash}
            ]

            # Display available upgrades
            y_offset = 150
            for i, upgrade in enumerate(upgrades):
                color = (100, 255, 100) if upgrade["name"] not in self.player.abilities else (
                150, 150, 150)  # Gray out if purchased
                upgrade_text = FONT.render(f"{i + 1}. {upgrade['name']} - {upgrade['cost']} Coins", True, color)
                self.screen.blit(upgrade_text, (WIDTH // 2 - 150, y_offset))
                y_offset += 50

            # Show player's current currency
            currency_text = FONT.render(f"Coins: {self.player.currency}", True, (255, 223, 0))
            self.screen.blit(currency_text, (WIDTH // 2 - 150, HEIGHT - 100))

            pygame.display.flip()

            # Handle shop interactions
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        shop_open = False  # Close shop and resume game
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        index = event.key - pygame.K_1  # Convert key to list index
                        selected_upgrade = upgrades[index]

                        if selected_upgrade["name"] not in self.player.actions and self.player.currency >= \
                                selected_upgrade["cost"]:
                            self.player.currency -= selected_upgrade["cost"]
                            self.player.actions.append(
                                selected_upgrade["name"])  # Store in actions instead of abilities
                            selected_upgrade["effect"]()  # Apply the ability

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
