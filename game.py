import pygame
import random
import sys
from player import Player
from enemy import Enemy, FastEnemy, TankEnemy, DasherEnemy, ShooterEnemy, SwarmEnemy  # Import all enemy types
from bossenemy import BossEnemy
from obstacle import generate_town_layout
from leaderboard import save_leaderboard

# Constants
WIDTH, HEIGHT = 1024, 768
MAP_WIDTH, MAP_HEIGHT = 2560, 1920
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

# Load the textures
FLOOR_TEXTURE = pygame.image.load("textures/StoneFloorTexture.png")  # Update with your file path
FLOOR_TEXTURE = pygame.transform.scale(FLOOR_TEXTURE, (128, 128))  # Resize to a smaller tile size

GRASS_TEXTURE = pygame.image.load("textures/grass.jpg")  # Update with your file path
GRASS_TEXTURE = pygame.transform.scale(GRASS_TEXTURE, (128, 128))  # Resize to a smaller tile size

WALL_TEXTURE = pygame.image.load("textures/wall.png")  # Update with actual file path
WALL_TEXTURE = pygame.transform.scale(WALL_TEXTURE, (30, 30))

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
        self.enemy_types = [Enemy]  # Start with only basic enemies
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

        self.boss_active = False

    def spawn_enemy(self):
        """Spawns enemies dynamically, but prevents spawns if the Boss is active."""
        if self.boss_active:
            return  # Do not spawn normal enemies when the Boss is alive

        enemy_weights = [3]  # Default: Normal enemies are common
        if FastEnemy in self.enemy_types:
            enemy_weights.append(2)
        if TankEnemy in self.enemy_types:
            enemy_weights.append(1)
        if DasherEnemy in self.enemy_types:
            enemy_weights.append(3)
        if ShooterEnemy in self.enemy_types:
            enemy_weights.append(2)
        if SwarmEnemy in self.enemy_types:
            enemy_weights.append(2)

        # Ensure enemy type selection remains valid
        if len(enemy_weights) != len(self.enemy_types):
            raise ValueError("Enemy weights do not match the available enemy types!")

        enemy_class = random.choices(self.enemy_types, weights=enemy_weights, k=1)[0]

        # Randomize spawn location
        base_x, base_y = random.choice([
            (random.randint(0, MAP_WIDTH), 0),
            (random.randint(0, MAP_WIDTH), MAP_HEIGHT),
            (0, random.randint(0, MAP_HEIGHT)),
            (MAP_WIDTH, random.randint(0, MAP_HEIGHT))
        ])

        # Handle special spawns like SwarmEnemy
        if enemy_class == Enemy:
            new_enemy = Enemy(base_x, base_y, 3)  # Normal enemies need health
        elif enemy_class == FastEnemy:
            new_enemy = FastEnemy(base_x, base_y)
        elif enemy_class == TankEnemy:
            new_enemy = TankEnemy(base_x, base_y)
        elif enemy_class == DasherEnemy:
            new_enemy = DasherEnemy(base_x, base_y)
        elif enemy_class == ShooterEnemy:
            new_enemy = ShooterEnemy(base_x, base_y)
        elif enemy_class == SwarmEnemy:
            swarm_group = []
            for i in range(5):  # Spawn a group of SwarmEnemies
                offset_x = random.randint(-30, 30)
                offset_y = random.randint(-30, 30)
                spawn_rect = pygame.Rect(base_x + offset_x, base_y + offset_y, 25, 25)
                if any(obstacle.collides(spawn_rect) for obstacle in self.obstacles):
                    continue
                swarm_member = SwarmEnemy(base_x + offset_x, base_y + offset_y, swarm_group)
                swarm_group.append(swarm_member)
                self.enemies.append(swarm_member)
            return  # Don't append new_enemy, since we added SwarmEnemies manually
        else:
            raise ValueError(f"Unknown enemy class: {enemy_class}")

        self.enemies.append(new_enemy)

    def new_wave(self):
        """Increases difficulty each wave, introducing new enemies and handling Boss waves."""
        self.wave += 1
        self.wave_start_time = pygame.time.get_ticks()

        # Boss Spawns at Wave 10 (or later if needed)
        if self.wave % 10 == 0 and self.wave != 0:
            print("⚠️ Boss Incoming! Normal enemies will stop spawning!")
            self.boss_active = True  # Set flag to prevent normal enemy spawns
            boss = BossEnemy(MAP_WIDTH // 2, MAP_HEIGHT // 2)  # Spawn Boss at center
            self.enemies.append(boss)
            return  # Skip normal wave logic

        # If the boss is active, do not spawn new waves
        if self.boss_active:
            return

        # Reduce the difficulty increase rate every 5 waves
        difficulty_modifier = max(0.5, 1 - (self.wave // 5) * 0.05)  # Slower reduction
        self.spawn_interval = max(500, int(INITIAL_SPAWN_INTERVAL * difficulty_modifier))

        print(f"Starting Wave {self.wave}! Spawn rate: {self.spawn_interval}ms")

        # Introduce new enemy types at wave milestones
        if self.wave == 2 and FastEnemy not in self.enemy_types:
            self.enemy_types.append(FastEnemy)
            print("Fast enemies introduced!")
        elif self.wave == 3 and TankEnemy not in self.enemy_types:
            self.enemy_types.append(TankEnemy)
            print("Tank enemies introduced!")
        elif self.wave == 5 and DasherEnemy not in self.enemy_types:
            self.enemy_types.append(DasherEnemy)
            print("Dashers introduced!")
        elif self.wave >= 7 and ShooterEnemy not in self.enemy_types:
            self.enemy_types.append(ShooterEnemy)
            print("Shooter enemies introduced!")
        elif self.wave >= 9 and SwarmEnemy not in self.enemy_types:
            self.enemy_types.append(SwarmEnemy)
            print("Swarm Enemies introduced!")

    def run(self):
        """Main game loop."""
        while self.running:
            self.draw_background()
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
                        self.player.use_dash()

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
                    enemy.update(self.player, self.obstacles, self, self.enemy_bullets)  # Pass bullets list
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
                        break  # ✅ Let bullet.py handle enemy damage & removal

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
            for enemy in self.enemies[:]:  # Iterate over a copy to avoid modification errors
                if enemy.rect is not None and enemy.rect.colliderect(self.player.rect):
                    self.player.take_damage()

                    # ✅ Only remove the enemy if it's NOT a BossEnemy
                    if not isinstance(enemy, BossEnemy):
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
            self.player.draw(self.screen, self.camera_x, self.camera_y, self)
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

            # Draw UI action elements
            self.draw_ability_ui()

            # Draw UI shop button
            self.draw_shop_ui()

            # Calculate XP progress width
            xp_progress_width = int((self.player.xp / self.player.xp_to_next_level) * XP_BAR_WIDTH)

            # Draw XP bar background (gray)
            pygame.draw.rect(self.screen, (100, 100, 100), (XP_BAR_X, XP_BAR_Y, XP_BAR_WIDTH, XP_BAR_HEIGHT))

            # Draw XP progress (blue)
            pygame.draw.rect(self.screen, (50, 150, 255), (XP_BAR_X, XP_BAR_Y, xp_progress_width, XP_BAR_HEIGHT))

            # 🏆 **Level Display**
            level_text = f"Lvl: {self.player.level}"
            level_text_x = XP_BAR_X + (XP_BAR_WIDTH - FONT.render(level_text, True, (255, 255, 255)).get_width()) // 2
            level_text_y = XP_BAR_Y + XP_BAR_HEIGHT + 5
            draw_text_with_border(self.screen, level_text, level_text_x, level_text_y, FONT)

            # 🌊 **Wave Display**
            wave_text_str = f"Wave: {self.wave}"  # Ensure this is a string
            draw_text_with_border(self.screen, wave_text_str, 10, 10, FONT)

            # 🎯 **Score Display**
            score_text_str = f"Score: {self.score}"  # Convert to string format
            draw_text_with_border(self.screen, score_text_str, WIDTH - 150, 10, FONT)

            # ❤️ **Health Display**
            health_text_str = f"Health: {self.player.health}"  # Ensure correct format
            draw_text_with_border(self.screen, health_text_str, 10, HEIGHT - 50, FONT)

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

        # Draw all game elements
        for bullet in self.player.bullets:
            bullet.draw(self.screen, self.camera_x, self.camera_y)
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x, self.camera_y)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen, self.camera_x, self.camera_y)
        self.player.draw(self.screen, self.camera_x, self.camera_y, self)

        # 2️⃣ Overlay a semi-transparent dark box to highlight the menu
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark transparent overlay
        self.screen.blit(overlay, (0, 0))

        # 3️⃣ Draw Level-Up UI on top
        level_up_text = "LEVEL UP! Choose an Upgrade:"
        level_up_surface = FONT.render(level_up_text, True, WHITE)
        level_up_x = (WIDTH - level_up_surface.get_width()) // 2  # Center horizontally
        draw_text_with_border(self.screen, level_up_text, level_up_x, 150, FONT)

        if self.player.pending_ability_choices:
            for i, ability in enumerate(self.player.pending_ability_choices, 1):  # ✅ Add a loop
                text = f"{i}: {ability['name']} - {ability['description']}"
                text_surface = FONT.render(text, True, WHITE)
                text_x = (WIDTH - text_surface.get_width()) // 2  # Center horizontally
                draw_text_with_border(self.screen, text, text_x, 200 + i * 50, FONT)

        pygame.display.flip()  # ✅ Now updates the screen without removing the game state

    def open_shop(self):
        """Pauses the game and displays the shop UI with a semi-transparent overlay and ESC button."""
        shop_open = True

        while shop_open:
            # ✅ 1️⃣ Keep the game scene visible by drawing everything first
            self.screen.fill((30, 30, 30))

            for bullet in self.player.bullets:
                bullet.draw(self.screen, self.camera_x, self.camera_y)
            for enemy in self.enemies:
                enemy.draw(self.screen, self.camera_x, self.camera_y)
            for obstacle in self.obstacles:
                obstacle.draw(self.screen, self.camera_x, self.camera_y)
            self.player.draw(self.screen, self.camera_x, self.camera_y, self)

            # ✅ 2️⃣ Overlay a semi-transparent dark box (like Upgrade Screen)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Dark transparent overlay
            self.screen.blit(overlay, (0, 0))

            # ✅ 3️⃣ Display "Shop" Title (Centered with Border)
            title_font = pygame.font.Font(None, 50)
            title_surface = title_font.render("SHOP", True, (255, 255, 255))
            title_x = (WIDTH - title_surface.get_width()) // 2  # Calculate center X
            draw_text_with_border(self.screen, "SHOP", title_x, 80, title_font)

            # ✅ 4️⃣ Draw ESC Button in the Top Right Corner (Properly Centered Text)
            esc_color = (200, 200, 200)  # Light gray ESC button
            esc_x, esc_y = WIDTH - 80, 20  # Position in top-right
            esc_width, esc_height = 60, 40
            esc_rect = pygame.Rect(esc_x, esc_y, esc_width, esc_height)

            # Draw semi-transparent background for ESC button
            esc_surface = pygame.Surface((esc_width, esc_height), pygame.SRCALPHA)
            pygame.draw.rect(esc_surface, (*esc_color, 50), (0, 0, esc_width, esc_height), border_radius=10)
            self.screen.blit(esc_surface, (esc_x, esc_y))

            # Draw ESC button outline
            pygame.draw.rect(self.screen, esc_color, esc_rect, border_radius=10, width=3)

            # 📝 **Properly center ESC text inside the button**
            esc_text_surface = FONT.render("ESC", True, (255, 255, 255))
            esc_text_x = esc_x + (esc_width - esc_text_surface.get_width()) // 2
            esc_text_y = esc_y + (esc_height - esc_text_surface.get_height()) // 2
            draw_text_with_border(self.screen, "ESC", esc_text_x, esc_text_y, FONT)

            # ✅ 5️⃣ Define available upgrades
            upgrades = [
                {"name": "Explosive Shot", "cost": 50, "effect": self.player.unlock_explosive_shot},
                {"name": "Sword Attack", "cost": 50, "effect": self.player.unlock_sword_attack},
                {"name": "Dash Ability", "cost": 25, "effect": self.player.unlock_dash}
            ]

            # ✅ 6️⃣ Find the longest text width dynamically for standardizing backdrops
            max_text_width = max(
                FONT.render(f"{i + 1}. {u['name']} - {u['cost']} Coins", True, (255, 255, 255)).get_width() for i, u in
                enumerate(upgrades))
            backdrop_width = max_text_width + 40  # Add padding
            backdrop_height = 35  # Standardized height
            backdrop_color = (20, 20, 20, 180)  # Semi-transparent dark gray

            # ✅ 7️⃣ Display available upgrades (Centered & Properly Positioned)
            y_offset = 200
            for i, upgrade in enumerate(upgrades):
                color = (100, 255, 100) if upgrade["name"] not in self.player.actions else (
                150, 150, 150)  # Gray if purchased
                text = f"{i + 1}. {upgrade['name']} - {upgrade['cost']} Coins"

                # 📦 **Draw backdrop rectangle centered around text**
                backdrop_x = (WIDTH - backdrop_width) // 2
                backdrop_rect = pygame.Surface((backdrop_width, backdrop_height), pygame.SRCALPHA)
                backdrop_rect.fill(backdrop_color)
                self.screen.blit(backdrop_rect, (backdrop_x, y_offset - 5))

                # 📝 **Draw text with border centered**
                text_surface = FONT.render(text, True, color)
                text_x = (WIDTH - text_surface.get_width()) // 2
                draw_text_with_border(self.screen, text, text_x, y_offset, FONT, color=color)
                y_offset += 50

            # ✅ 8️⃣ Show player's current currency at the bottom (Centered)
            currency_text = f"Coins: {self.player.currency}"
            currency_surface = FONT.render(currency_text, True, (255, 223, 0))
            currency_x = (WIDTH - currency_surface.get_width()) // 2
            draw_text_with_border(self.screen, currency_text, currency_x, HEIGHT - 100, FONT, color=(255, 223, 0))

            pygame.display.flip()

            # ✅ 9️⃣ Handle shop interactions
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

            # ✅ 8️⃣ Handle shop interactions
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

    def draw_ability_ui(self):
        """Displays UI elements for purchased abilities with proper cooldown indicators."""
        ability_icons = {
            "Explosive Shot": ("Q", (255, 0, 0), "explosive_shot"),  # Red for explosive shot
            "Sword Attack": ("E", (0, 0, 255), None),  # No cooldown key, handled separately
            "Dash Ability": ("Shift", (0, 255, 0), "dash")  # Green for dash
        }

        x_offset = WIDTH - 875  # Align abilities correctly
        y_position = HEIGHT - 60  # Bottom of the screen

        current_time = pygame.time.get_ticks()

        for ability in self.player.actions:
            if ability in ability_icons:
                key, color, cooldown_key = ability_icons[ability]

                # Define button sizes
                button_width = 80 if ability == "Dash Ability" else 50  # Wider bar for Shift key
                button_height = 40
                button_rect = pygame.Rect(x_offset, y_position, button_width, button_height)

                # 🎨 **Draw the ability button with rounded edges**
                fill_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
                pygame.draw.rect(fill_surface, (*color, 50), (0, 0, button_width, button_height), border_radius=10)
                self.screen.blit(fill_surface, (x_offset, y_position))

                pygame.draw.rect(self.screen, color, button_rect, border_radius=10, width=3)  # Outline

                # 🔥 **Cooldown logic: Darken button when on cooldown**
                if cooldown_key:
                    if current_time < self.player.cooldowns[cooldown_key]:
                        cooldown_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
                        pygame.draw.rect(cooldown_surface, (0, 0, 0, 150), (0, 0, button_width, button_height),
                                         border_radius=10)
                        self.screen.blit(cooldown_surface, (x_offset, y_position))
                else:
                    # Special case for Sword Attack cooldown
                    if current_time - self.player.sword_attack.last_attack_time < self.player.sword_attack.cooldown:
                        cooldown_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
                        pygame.draw.rect(cooldown_surface, (0, 0, 0, 150), (0, 0, button_width, button_height),
                                         border_radius=10)
                        self.screen.blit(cooldown_surface, (x_offset, y_position))

                # 📝 **Draw keybind text with a border**
                key_text_surface = FONT.render(key, True, (255, 255, 255))  # White text
                key_text_x = x_offset + (button_width - key_text_surface.get_width()) // 2
                key_text_y = y_position + (button_height - key_text_surface.get_height()) // 2
                draw_text_with_border(self.screen, key, key_text_x, key_text_y, FONT)

                x_offset += button_width + 10  # Space out buttons

    def draw_shop_ui(self):
        """Displays the shop button and currency counter in the bottom-right corner."""
        shop_key = "B"
        shop_color = (255, 215, 0)  # Gold color for the shop button

        x_position = WIDTH - 150  # Keep text in place
        y_position = HEIGHT - 100  # Above the currency display
        button_x_position = x_position + 50  # Move only the button to the right

        # Define button size
        button_width = 50
        button_height = 40
        button_rect = pygame.Rect(button_x_position, y_position, button_width, button_height)

        # 🏪 **Draw gold rounded shop button**
        fill_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        pygame.draw.rect(fill_surface, (*shop_color, 50), (0, 0, button_width, button_height), border_radius=10)
        self.screen.blit(fill_surface, (button_x_position, y_position))

        pygame.draw.rect(self.screen, shop_color, button_rect, border_radius=10, width=3)  # Outline

        # 🎯 **Properly center the "B" key inside the button**
        key_text_surface = FONT.render(shop_key, True, (255, 255, 0))
        key_text_x = button_x_position + (button_width - key_text_surface.get_width()) // 2
        key_text_y = y_position + (button_height - key_text_surface.get_height()) // 2
        draw_text_with_border(self.screen, shop_key, key_text_x, key_text_y, FONT)

        # 🏷 **Draw "Shop:" label with a border for better visibility**
        shop_label = "Shop:"
        shop_label_surface = FONT.render(shop_label, True, (255, 255, 255))
        shop_label_x = x_position - 30
        shop_label_y = y_position + 5
        draw_text_with_border(self.screen, shop_label, shop_label_x, shop_label_y, FONT)

        # 💰 **Draw currency counter below the shop button with a border**
        currency_text = f"Currency: {self.player.currency}"
        currency_surface = FONT.render(currency_text, True, (255, 223, 0))  # Gold text
        currency_x = x_position - 30
        currency_y = y_position + 50
        draw_text_with_border(self.screen, currency_text, currency_x, currency_y, FONT)

    # Function to draw the background
    def draw_background(self):
        camera_x, camera_y = self.camera_x, self.camera_y  # Get camera offset

        # Get tile sizes
        grass_tile_w = GRASS_TEXTURE.get_width()
        grass_tile_h = GRASS_TEXTURE.get_height()
        floor_tile_w = FLOOR_TEXTURE.get_width()
        floor_tile_h = FLOOR_TEXTURE.get_height()

        for x in range(0, MAP_WIDTH, floor_tile_w):
            for y in range(0, MAP_HEIGHT, floor_tile_h):
                self.screen.blit(FLOOR_TEXTURE, (x - camera_x, y - camera_y))

        for x in range(-grass_tile_w * 5, MAP_WIDTH + grass_tile_w * 5, grass_tile_w):
            for y in range(-grass_tile_h * 5, MAP_HEIGHT + grass_tile_h * 5, grass_tile_h):
                # Ensure grass is **only drawn outside the playable area**
                if x < 0 or y < 0 or x >= MAP_WIDTH or y >= MAP_HEIGHT:
                    self.screen.blit(GRASS_TEXTURE, (x - camera_x, y - camera_y))


        # Draw Walls
        border_thickness = 10

        for x in range(0, MAP_WIDTH, WALL_TEXTURE.get_width()):
            self.screen.blit(WALL_TEXTURE, (x - camera_x, -camera_y))  # Top
            self.screen.blit(WALL_TEXTURE, (x - camera_x, MAP_HEIGHT - camera_y - border_thickness))  # Bottom

        for y in range(0, MAP_HEIGHT, WALL_TEXTURE.get_height()):
            self.screen.blit(WALL_TEXTURE, (-camera_x, y - camera_y))  # Left
            self.screen.blit(WALL_TEXTURE, (MAP_WIDTH - camera_x - border_thickness, y - camera_y))  # Right

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

def draw_text_with_border(screen, text, x, y, font, color=(255, 255, 255), border_color=(0, 0, 0)):
    """Draws outlined text for better visibility."""
    text_surface = font.render(text, True, color)
    outline_surface = font.render(text, True, border_color)

    # Draw outline (4-way offset for thickness)
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        screen.blit(outline_surface, (x + dx, y + dy))

    # Draw main text
    screen.blit(text_surface, (x, y))