import pygame
import math
from shooterbullet import ShooterBullet

ENEMY_SPEED = 2  # Base enemy speed

class Enemy:
    """Base enemy class with HP system, hit effects, and a brief death animation."""
    def __init__(self, x, y, health):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = ENEMY_SPEED
        self.health = health
        self.max_health = health  # Store max HP for health bar calculations
        self.hit_timer = 0  # Timer for hit flash effect
        self.hit_effect_duration = 75  # Flash effect duration (75ms)
        self.death_timer = None  # Tracks when enemy dies
        self.death_effect_duration = 100  # Time to show death effect (100ms)
        self.is_dying = False  # Flag to track if enemy is in the death phase

    def take_damage(self, damage=1):
        """Reduces HP when hit. If health reaches zero, starts death effect."""
        self.health -= damage
        self.hit_timer = pygame.time.get_ticks()  # Start hit effect timer

        if self.health <= 0 and not self.is_dying:
            self.is_dying = True
            self.death_timer = pygame.time.get_ticks()  # Start death effect timer
            return True  # Now correctly returns True when enemy is dead

        return False  # Otherwise, return False

    def update(self, player, obstacles):
        """Updates enemy movement, but stops moving if dying."""
        if self.is_dying or self.rect is None:
            return  # No movement if in death phase

        dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)

        move_x = self.speed * math.cos(angle)
        move_y = self.speed * math.sin(angle)

        old_x, old_y = self.rect.x, self.rect.y

        # Try moving in X first
        self.rect.x += move_x
        if any(obstacle.collides(self.rect) for obstacle in obstacles):
            self.rect.x = old_x  # Undo move if collision occurs

        # Try moving in Y second
        self.rect.y += move_y
        if any(obstacle.collides(self.rect) for obstacle in obstacles):
            self.rect.y = old_y  # Undo move if collision occurs

    def draw(self, screen, camera_x, camera_y):
        """Draws the enemy, adding hit and death effects."""
        if self.rect is None:
            return  # Don't draw if the enemy is considered 'removed'

        current_time = pygame.time.get_ticks()

        # If hit recently, flash white
        if current_time - self.hit_timer < self.hit_effect_duration:
            color = (255, 255, 255)  # White flash
        elif self.is_dying:
            color = (255, 255, 255)  # White flash on death

            # Check if death effect time has passed
            if current_time - self.death_timer > self.death_effect_duration:
                self.rect = None  # Completely remove the enemy
                return

        else:
            color = (255, 0, 0)  # Normal enemy color

        # (Optional) Shrink enemy slightly when dying
        if self.is_dying:
            shrink_factor = 0.75  # Reduce size by 25% during death animation
            width, height = int(self.rect.width * shrink_factor), int(self.rect.height * shrink_factor)
            draw_x = self.rect.x - camera_x + (self.rect.width - width) // 2
            draw_y = self.rect.y - camera_y + (self.rect.height - height) // 2
        else:
            width, height = self.rect.width, self.rect.height
            draw_x = self.rect.x - camera_x
            draw_y = self.rect.y - camera_y

        pygame.draw.rect(
            screen,
            color,
            pygame.Rect(draw_x, draw_y, width, height)
        )

        # Draw health bar only if not dying
        if not self.is_dying:
            self.draw_health_bar(screen, camera_x, camera_y, color)

    def draw_health_bar(self, screen, camera_x, camera_y, color):
        """Draws a health bar above the enemy."""
        if self.health > 0:
            health_bar_width = int((self.health / self.max_health) * self.rect.width)
            pygame.draw.rect(screen, (0, 255, 0),  # Green health bar
                             pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y - 5, health_bar_width, 3))

class FastEnemy(Enemy):
    """Smaller, faster enemy with 1 HP."""
    def __init__(self, x, y):
        super().__init__(x, y, 1)  # Fast enemies have 1 HP
        self.rect = pygame.Rect(x, y, 30, 30)  # Smaller size
        self.speed = ENEMY_SPEED * 1.8  # Faster speed

    def draw(self, screen, camera_x, camera_y):
        current_time = pygame.time.get_ticks()

        if current_time - self.hit_timer < self.hit_effect_duration:
            color = (255, 255, 255)  # White flash when hit
        else:
            color = (255, 255, 0)  # Default yellow

        pygame.draw.rect(screen, color, pygame.Rect(
            self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height
        ))
        self.draw_health_bar(screen, camera_x, camera_y, color)


class TankEnemy(Enemy):
    """Bigger, slower enemy with 5 HP."""
    def __init__(self, x, y):
        super().__init__(x, y, 5)  # Tank enemies have 5 HP
        self.rect = pygame.Rect(x, y, 50, 50)  # Bigger size
        self.speed = ENEMY_SPEED * 0.75  # Slower movement

    def draw(self, screen, camera_x, camera_y):
        current_time = pygame.time.get_ticks()

        if current_time - self.hit_timer < self.hit_effect_duration:
            color = (255, 255, 255)  # White flash when hit
        else:
            color = (0, 0, 225)  # Default blue

        pygame.draw.rect(screen, color, pygame.Rect(
            self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height
        ))
        self.draw_health_bar(screen, camera_x, camera_y, color)

class DasherEnemy(Enemy):
    """Enemy that dashes when close to the player."""
    def __init__(self, x, y):
        super().__init__(x, y, 3)  # 3 HP, same as normal enemies
        self.rect = pygame.Rect(x, y, 35, 35)  # Slightly smaller hitbox
        self.base_speed = ENEMY_SPEED * 1  # Normal movement speed
        self.dash_speed = ENEMY_SPEED * 25  # Much faster dash speed
        self.speed = self.base_speed
        self.dash_cooldown = 2000  # 2-second cooldown between dashes
        self.charge_time = 500  # 0.5-second warning before dashing
        self.last_dash_time = pygame.time.get_ticks()
        self.is_charging = False
        self.charge_start_time = 0

    def update(self, player, obstacles):
        """Updates movement, initiating a charge-up visual before dashing."""
        current_time = pygame.time.get_ticks()
        distance_to_player = math.sqrt((player.rect.centerx - self.rect.centerx) ** 2 + (player.rect.centery - self.rect.centery) ** 2)

        # Start charging phase if close enough and cooldown is up
        if distance_to_player < 125 and current_time - self.last_dash_time > self.dash_cooldown and not self.is_charging:
            self.is_charging = True
            self.charge_start_time = current_time  # Store charge start time
            self.speed = 0  # Stop moving during charge phase

        # After charge_time, actually dash
        if self.is_charging and current_time - self.charge_start_time > self.charge_time:
            self.is_charging = False
            self.speed = self.dash_speed
            self.last_dash_time = current_time  # Reset cooldown

        # If not charging, return to normal movement speed
        elif not self.is_charging:
            self.speed = self.base_speed

        # Steering movement logic
        dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)

        move_x = self.speed * math.cos(angle)
        move_y = self.speed * math.sin(angle)

        old_x, old_y = self.rect.x, self.rect.y

        # Try moving in X first
        self.rect.x += move_x
        if any(obstacle.collides(self.rect) for obstacle in obstacles):
            self.rect.x = old_x  # Undo move if collision occurs

        # Try moving in Y second
        self.rect.y += move_y
        if any(obstacle.collides(self.rect) for obstacle in obstacles):
            self.rect.y = old_y  # Undo move if collision occurs

    def draw(self, screen, camera_x, camera_y):
        """Draws the dasher enemy with a visual cue when charging and hit feedback."""
        current_time = pygame.time.get_ticks()

        # Flash white if recently hit
        if current_time - self.hit_timer < self.hit_effect_duration:
            color = (255, 255, 255)  # White flash on hit
        elif self.is_charging:
            color = (255, 255, 0)  # Bright yellow when charging
        else:
            color = (255, 100, 100)  # Default pinkish-red color

        pygame.draw.rect(
            screen,
            color,
            pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height)
        )

        # Draw health bar
        self.draw_health_bar(screen, camera_x, camera_y, color)

class ShooterEnemy(Enemy):
    """An enemy that moves into range, stops, and shoots bullets at the player."""
    def __init__(self, x, y):
        super().__init__(x, y, 3)  # Shooter has 3 HP
        self.rect = pygame.Rect(x, y, 35, 35)  # Slightly smaller than normal enemies
        self.attack_range = 300  # Stops moving when within 300 pixels of player
        self.shoot_cooldown = 2000  # Fires every 2 seconds
        self.last_shot_time = pygame.time.get_ticks()  # Track last shot time
        self.speed = ENEMY_SPEED * 0.8  # Moves slightly slower than normal enemies

    def update(self, player, obstacles, enemy_bullets):
        """Updates movement and shooting behavior."""
        current_time = pygame.time.get_ticks()
        distance_to_player = math.sqrt(
            (player.rect.centerx - self.rect.centerx) ** 2 +
            (player.rect.centery - self.rect.centery) ** 2
        )

        if distance_to_player > self.attack_range:
            # Move towards the player if out of range
            dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
            angle = math.atan2(dy, dx)
            move_x = self.speed * math.cos(angle)
            move_y = self.speed * math.sin(angle)

            old_x, old_y = self.rect.x, self.rect.y

            # Try moving in X first
            self.rect.x += move_x
            if any(obstacle.collides(self.rect) for obstacle in obstacles):
                self.rect.x = old_x  # Undo move if collision occurs

            # Try moving in Y second
            self.rect.y += move_y
            if any(obstacle.collides(self.rect) for obstacle in obstacles):
                self.rect.y = old_y  # Undo move if collision occurs

        else:
            # If within range, stop and shoot
            if current_time - self.last_shot_time > self.shoot_cooldown:
                enemy_bullets.append(ShooterBullet(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery))
                self.last_shot_time = current_time  # Reset cooldown

    def draw(self, screen, camera_x, camera_y):
        """Draws the shooter enemy."""
        current_time = pygame.time.get_ticks()

        if current_time - self.hit_timer < self.hit_effect_duration:
            color = (255, 255, 255)  # Flash white when hit
        else:
            color = (150, 0, 255)  # Purple color for shooter

        pygame.draw.rect(
            screen,
            color,
            pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height)
        )

        self.draw_health_bar(screen, camera_x, camera_y, color)


class DeathAnimation:
    """Handles the death animation effect."""
    def __init__(self, x, y, size=40, duration=500):
        self.rect = pygame.Rect(x, y, size, size)  # Same size as enemy
        self.start_time = pygame.time.get_ticks()  # Track when animation starts
        self.duration = duration  # How long the effect lasts in ms
        self.alpha = 255  # Opacity for fade effect
        print(f"Death animation created at {x}, {y}")  # Debugging

    def update(self):
        """Updates the animation effect (e.g., fading out)."""
        elapsed_time = pygame.time.get_ticks() - self.start_time
        self.alpha = max(255 - (elapsed_time / self.duration) * 255, 0)  # Fade out effect

        return elapsed_time > self.duration  # Returns True when animation is done

    def draw(self, screen, camera_x, camera_y):
        """Draws the animation effect."""
        temp_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        temp_surface.fill((255, 255, 255, int(self.alpha)))  # White fading out
        screen.blit(temp_surface, (self.rect.x - camera_x, self.rect.y - camera_y))


