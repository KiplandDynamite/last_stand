import pygame
import math
import random
from bullet import Bullet
from abilities import ABILITY_LIST
from swordattack import SwordAttack

BORDER_THICKNESS = 10  # Matches the visual border thickness


class Player:
    def __init__(self, x, y, map_width, map_height):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.health = 3
        self.bullets = []
        self.MAP_WIDTH = map_width
        self.MAP_HEIGHT = map_height
        self.xp = 0  # XP system
        self.level = 1
        self.xp_to_next_level = 100  # Starting XP threshold
        self.currency = 100
        self.pending_ability_choices = []
        self.cooldowns = {"explosive_shot": 0, "sword_attack": 0, "dash": 0}
        self.abilities = []  # Holds selected abilities
        self.actions = []  # Stores shop abilities
        self.base_speed = 5
        self.speed = self.base_speed

        self.sword_attack = SwordAttack(self)

        self.move_speed_bonus = 0

        self.adrenaline_boost = 0.00  # ✅ Starts at 0%, increases with Adrenaline Rush upgrades
        self.adrenaline_active = False  # ✅ Whether Adrenaline Rush is active
        self.adrenaline_end_time = 0

        self.bonus_bullets = 0  # ✅ Track extra bullets
        self.queued_shots = []  # ✅ Store bullets with delay
        self.shot_delay = 120  # ✅ Delay between extra bullets (in milliseconds)
        self.pierce = 0  # ✅ Track number of pierces
        self.fire_rate_multiplier = 1.0  # ✅ Default is 1.0 (no boost)
        self.last_shot_time = 0  # ✅ Tracks when the last shot was fired

        self.ricochet_count = 0

        self.dash_active = False  # ✅ Track if dashing
        self.dash_end_time = 0  # ✅ When the dash should end
        self.dash_vector = pygame.Vector2(0, 0)  # ✅ Store dash direction

        # Hit effect tracking
        self.hit_timer = 0  # Time when player was last hit
        self.hit_effect_duration = 150  # Flash effect duration in milliseconds

    def update(self, obstacles, game):
        keys = pygame.key.get_pressed()

        # Move (PRESS WASD)
        move_x, move_y = 0, 0
        if keys[pygame.K_w]: move_y -= self.speed
        if keys[pygame.K_s]: move_y += self.speed
        if keys[pygame.K_a]: move_x -= self.speed
        if keys[pygame.K_d]: move_x += self.speed

        # ✅ If dashing, override movement
        if self.dash_active:
            self.rect.x += self.dash_vector.x
            self.rect.y += self.dash_vector.y

            if pygame.time.get_ticks() >= self.dash_end_time:
                self.dash_active = False  # ✅ End dash after duration

        # Try moving in X first
        old_x = self.rect.x
        self.rect.x += move_x
        if any(obstacle.collides(self.rect) for obstacle in obstacles):
            self.rect.x = old_x  # Undo move if collision occurs

        # Try moving in Y second
        old_y = self.rect.y
        self.rect.y += move_y
        if any(obstacle.collides(self.rect) for obstacle in obstacles):
            self.rect.y = old_y  # Undo move if collision occurs

        # Clamp position inside game boundaries
        self.rect.x = max(BORDER_THICKNESS, min(self.rect.x, self.MAP_WIDTH - self.rect.width - BORDER_THICKNESS))
        self.rect.y = max(BORDER_THICKNESS, min(self.rect.y, self.MAP_HEIGHT - self.rect.height - BORDER_THICKNESS))

        current_time = pygame.time.get_ticks()

        self.sword_attack.update(game.enemies, game)

        # ✅ Always apply Speed Boost permanently
        self.speed = self.base_speed * (1 + self.move_speed_bonus)

        # ✅ Apply temporary Adrenaline Rush bonus if active
        if self.adrenaline_active:
            self.speed *= (1 + self.adrenaline_boost)  # ✅ Dynamically modify speed while active

        if self.adrenaline_active and current_time > self.adrenaline_end_time:
            self.adrenaline_active = False
            print("🔴 Adrenaline Rush ENDED! Speed Reset.")

            # ✅ Instead of resetting `adrenaline_boost` to 0, keep the stacked value
            adrenaline_upgrades = self.abilities.count("Adrenaline Rush")
            self.adrenaline_boost = 0.2 * adrenaline_upgrades  # ✅ Maintain stacking

        # ✅ Secret Dev Command: Instant Level Up
        if keys[pygame.K_l]:
            print("🛠 DEV COMMAND: Instant Level Up Activated!")
            self.force_level_up(game)  # ✅ Calls a dedicated function to handle dev level-up

    def shoot(self, mouse_x, mouse_y):
        """Shoots bullets, reducing delay with Rapid Fire stacks."""
        current_time = pygame.time.get_ticks()
        fire_delay = int(300 / self.fire_rate_multiplier)  # ✅ Adjust delay based on fire rate

        if current_time - self.last_shot_time < fire_delay:
            return  # ⛔ Prevents shooting if delay hasn't passed

        self.last_shot_time = current_time  # ✅ Update last shot time

        # Calculate bullet direction
        angle = math.atan2(mouse_y - self.rect.centery, mouse_x - self.rect.centerx)

        # Fire primary bullet
        bullet = Bullet(self.rect.centerx, self.rect.centery, angle, self.MAP_WIDTH, self.MAP_HEIGHT, self.pierce,0, self.ricochet_count)
        bullet.fire()
        self.bullets.append(bullet)

        # Queue additional bullets with delay
        for i in range(self.bonus_bullets):
            delay_time = current_time + ((i + 1) * 50)  # ✅ Adjusted to match new fire rate scaling
            self.queued_shots.append((delay_time, angle, self.ricochet_count))


    def update_bullets(self):
        """Processes queued bullets and fires them when the delay is reached."""
        current_time = pygame.time.get_ticks()
        shots_to_fire = []  # Store bullets that need to be fired

        for shot in self.queued_shots[:]:  # Iterate safely over queued shots
            shot_time, angle, ricochet_count = shot
            if current_time >= shot_time:
                # ✅ Create and immediately fire the extra bullet
                bullet = Bullet(self.rect.centerx, self.rect.centery, angle, self.MAP_WIDTH, self.MAP_HEIGHT,
                                self.pierce,0, ricochet_count)
                bullet.fire()  # ✅ Ensure bullet is set to active
                self.bullets.append(bullet)
                shots_to_fire.append(shot)  # ✅ Mark this shot for removal


        # ✅ Remove fired shots from the queue
        for shot in shots_to_fire:
            self.queued_shots.remove(shot)

    def take_damage(self):
        """Reduces health on collision with enemies and starts hit effect."""
        self.health -= 1
        self.hit_timer = pygame.time.get_ticks()  # Start hit effect timer

    def draw(self, screen, camera_x, camera_y, game):
        """Draws the player with a bold black outline and a flashing hit effect when damaged."""
        current_time = pygame.time.get_ticks()
        time_since_hit = current_time - self.hit_timer

        flash_interval = 75  # Time between flashes in milliseconds
        flashes = 3  # Number of flashes during damage effect
        outline_color = (0, 0, 0)  # Default black outline
        base_color = (0, 255, 0, 255)  # Normal solid green

        # Determine damage effect color
        if time_since_hit < self.hit_effect_duration:
            if (time_since_hit // flash_interval) % 2 == 0:
                player_color = (255, 255, 255, 180)  # Semi-transparent white flash
                outline_color = (255, 0, 0)  # Red outline when hit
            else:
                player_color = (0, 255, 0, 180)  # Semi-transparent green
        else:
            player_color = base_color  # Normal color

        # Draw outline slightly larger than before
        pygame.draw.rect(screen, outline_color,
                         pygame.Rect(self.rect.x - camera_x - 3, self.rect.y - camera_y - 3,
                                     self.rect.width + 6, self.rect.height + 6))

        # Draw player with transparency support
        player_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        player_surface.fill(player_color)
        screen.blit(player_surface, (self.rect.x - camera_x, self.rect.y - camera_y))

        self.sword_attack.draw(screen, game)

    def gain_xp(self, amount, game):
        """Increase XP and check for level-up. Also triggers Adrenaline Rush on kill."""
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            self.level_up(game)

        # Debugging: Check if Adrenaline Rush is in abilities
        print(f"📊 Current Abilities: {self.abilities}")

        if "Adrenaline Rush" in self.abilities:
            if not self.adrenaline_active:
                self.adrenaline_active = True
                self.adrenaline_end_time = pygame.time.get_ticks() + 5000  # ✅ Refresh 5s timer
                print(f"🔥 Adrenaline Rush ACTIVATED! Speed Boost: +{int(self.adrenaline_boost * 100)}%")

                # ✅ Stack Adrenaline Rush Effect
                adrenaline_upgrades = self.abilities.count("Adrenaline Rush")  # Count how many times it was selected
                self.adrenaline_boost = 0.2 * adrenaline_upgrades  # ✅ Increase boost per stack
                print(
                    f"🔥 Adrenaline Rush Stack Count: {adrenaline_upgrades}, New Boost: +{int(self.adrenaline_boost * 100)}%")

    def level_up(self, game):
        """Handles level-up logic and presents upgrade choices."""
        self.xp -= self.xp_to_next_level  # Carry over excess XP
        self.level += 1
        self.xp_to_next_level = int(self.xp_to_next_level * 1.2)  # Increase XP threshold
        self.choose_upgrade(game)

    def choose_upgrade(self, game):
        """Presents 3 random upgrade choices and pauses the game until player selects."""
        options = random.sample(ABILITY_LIST, 3)  # Pick 3 random abilities
        self.pending_ability_choices = options  # Store choices
        game.paused_for_upgrade = True  # Pause game until player picks

        print(f"LEVEL UP! Choose an upgrade:")
        for i, ability in enumerate(options, 1):
            print(f"{i}: {ability['name']} - {ability['description']}")

    def handle_level_up_input(self, key, game):
        """Handles player's input for choosing an ability and resumes the game."""
        if not self.pending_ability_choices:
            return  # No upgrade to select

        if key in (pygame.K_1, pygame.K_2, pygame.K_3):
            index = key - pygame.K_1  # Convert key to list index
            selected_ability = self.pending_ability_choices[index]

            print(f"Selected: {selected_ability['name']}!")  # Debug
            selected_ability["effect"](self)  # Apply power-up effect
            self.abilities.append(selected_ability["name"])
            self.pending_ability_choices = []  # Clear choices
            game.paused_for_upgrade = False  # Resume the game

    def unlock_explosive_shot(self):
        """Unlocks the explosive shot ability."""
        if "Explosive Shot" not in self.abilities:
            self.abilities.append("Explosive Shot")
            print("🔥 Explosive Shot Unlocked!")

    def use_explosive_shot(self, mouse_x, mouse_y, game):
        """Fires an explosive shot that explodes on impact, dealing AoE damage."""
        if "Explosive Shot" in self.actions and pygame.time.get_ticks() >= self.cooldowns["explosive_shot"]:
            print("💥 Explosive Shot Fired!")
            self.cooldowns["explosive_shot"] = pygame.time.get_ticks() + 2000 # 2 sec cooldown

            # ✅ Calculate bullet direction using passed mouse coordinates
            angle = math.atan2(mouse_y - self.rect.centery, mouse_x - self.rect.centerx)

            print(
                f"🎯 Aiming: Player ({self.rect.centerx}, {self.rect.centery}) -> Mouse ({mouse_x}, {mouse_y}), Angle: {math.degrees(angle)}°")

            # ✅ Create explosive bullet
            bullet = Bullet(self.rect.centerx, self.rect.centery, angle, self.MAP_WIDTH, self.MAP_HEIGHT,
                            self.pierce, 0, self.ricochet_count, explosive=True)  # ✅ Explosive flag
            bullet.fire()
            self.bullets.append(bullet)

    def unlock_sword_attack(self):
        """Unlocks the sword attack ability."""
        if "Sword Attack" not in self.abilities:
            self.abilities.append("Sword Attack")
            print("⚔️ Sword Attack Unlocked!")

    def use_sword_attack(self, game):
        """Performs a melee slash if off cooldown."""
        if "Sword Attack" in self.actions and self.sword_attack.can_attack():
            print("⚔️ Sword Slash Initiated!")
            self.sword_attack.start_attack()

    def unlock_dash(self):
        """Unlocks the dash ability."""
        if "Dash" not in self.abilities:
            self.abilities.append("Dash")
            print("💨 Dash Ability Unlocked!")
            self.dash_active = False  # ✅ Track if dashing
            self.dash_end_time = 0  # ✅ When the dash should end
            self.dash_vector = pygame.Vector2(0, 0)  # ✅ Store dash direction

    def use_dash(self):
        """Allows the player to dash in the current movement direction if off cooldown."""
        current_time = pygame.time.get_ticks()

        if "Dash" in self.abilities and not self.dash_active and current_time >= self.cooldowns["dash"]:
            move_x, move_y = 0, 0
            keys = pygame.key.get_pressed()

            if keys[pygame.K_w]: move_y -= 1
            if keys[pygame.K_s]: move_y += 1
            if keys[pygame.K_a]: move_x -= 1
            if keys[pygame.K_d]: move_x += 1

            if move_x == 0 and move_y == 0:
                return  # ⛔ Prevent dashing if not moving

            print("💨 Dashing!")

            # ✅ Normalize vector to maintain consistent speed across angles
            self.dash_vector = pygame.Vector2(move_x, move_y).normalize() * 10  # 10 units per frame
            self.dash_active = True
            self.dash_end_time = current_time + 200  # Dash lasts 200ms
            self.cooldowns["dash"] = current_time + 5000  # Set cooldown (5 sec)

    def force_level_up(self, game):
        """Dev command to instantly level up and pick an ability."""
        self.xp = self.xp_to_next_level  # ✅ Sets XP to exactly what is needed to level up
        self.level_up(game)  # ✅ Triggers the level-up sequence
