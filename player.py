import pygame
import math
import random
from bullet import Bullet
from abilities import ABILITY_LIST

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
        self.pending_ability_choices = []
        self.abilities = []  # Holds selected abilities
        self.speed = 5

        self.bonus_bullets = 0  # ✅ Track extra bullets
        self.pierce = 0  # ✅ Track number of pierces
        self.queued_shots = []  # ✅ Store bullets with delay
        self.shot_delay = 120  # ✅ Delay between extra bullets (in milliseconds)

        # Hit effect tracking
        self.hit_timer = 0  # Time when player was last hit
        self.hit_effect_duration = 150  # Flash effect duration in milliseconds

    def update(self, obstacles):
        keys = pygame.key.get_pressed()

        move_x, move_y = 0, 0
        if keys[pygame.K_w]: move_y -= self.speed
        if keys[pygame.K_s]: move_y += self.speed
        if keys[pygame.K_a]: move_x -= self.speed
        if keys[pygame.K_d]: move_x += self.speed

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

    def shoot(self, mouse_x, mouse_y):
        """Shoots bullets with a delay for extra shots while keeping smooth gameplay."""
        angle = math.atan2(mouse_y - self.rect.centery, mouse_x - self.rect.centerx)
        current_time = pygame.time.get_ticks()

        # Fire the first bullet instantly
        bullet = Bullet(self.rect.centerx, self.rect.centery, angle, self.MAP_WIDTH, self.MAP_HEIGHT, self.pierce)
        bullet.fire()  # ✅ Ensure instant bullets are fired
        self.bullets.append(bullet)

        # Queue additional bullets with delay
        for i in range(self.bonus_bullets):
            delay_time = current_time + ((i + 1) * 50)  # ✅ Slightly increase delay for visibility
            self.queued_shots.append((delay_time, angle))  # ✅ Store correctly

    def update_bullets(self):
        """Processes queued bullets and fires them when the delay is reached."""
        current_time = pygame.time.get_ticks()
        shots_to_fire = []  # Store bullets that need to be fired

        for shot in self.queued_shots[:]:  # Iterate safely over queued shots
            shot_time, angle = shot  # Extract stored shot data
            if current_time >= shot_time:
                # ✅ Create and immediately fire the extra bullet
                bullet = Bullet(self.rect.centerx, self.rect.centery, angle, self.MAP_WIDTH, self.MAP_HEIGHT,
                                self.pierce)
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

    def draw(self, screen, camera_x, camera_y):
        """Draws the player with a flashing hit effect when damaged."""
        current_time = pygame.time.get_ticks()
        time_since_hit = current_time - self.hit_timer

        if time_since_hit < self.hit_effect_duration:
            flash_interval = 75  # Time between flashes in milliseconds
            flashes = 3  # Number of flashes

            # Determine whether to flash white or be slightly red & transparent
            if (time_since_hit // flash_interval) % 2 == 0:
                color = (255, 255, 255, 180)  # Semi-transparent white flash
            else:
                color = (0, 255, 0, 180)  # Semi-transparent red
        else:
            color = (0, 255, 0, 255)  # Normal solid green

        # Draw player with potential transparency
        player_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        player_surface.fill(color)
        screen.blit(player_surface, (self.rect.x - camera_x, self.rect.y - camera_y))

    def gain_xp(self, amount, game):
        """Increase XP and check for level-up."""
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            self.level_up(game)

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
            self.abilities.append(selected_ability)  # Store chosen ability
            self.pending_ability_choices = []  # Clear choices
            game.paused_for_upgrade = False  # Resume the game
