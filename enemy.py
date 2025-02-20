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
        print(f"Enemy took {damage} dmg!")
        self.hit_timer = pygame.time.get_ticks()  # Start hit effect timer

        if self.health <= 0 and not self.is_dying:
            self.is_dying = True
            self.death_timer = pygame.time.get_ticks()  # Start death effect timer
            return True  # Now correctly returns True when enemy is dead

        return False  # Otherwise, return False

    def update(self, player, obstacles, game):
        """Updates enemy movement and handles death removal."""

        if self.is_dying:
            # ✅ Remove enemy if death effect is finished
            if pygame.time.get_ticks() - self.death_timer > 100:  # Adjust delay as needed
                print(f"💀 Enemy removed at {self.rect.topleft}")
                game.enemies.remove(self)  # ✅ Now actually removes the enemy
            return  # ✅ Prevents further updates

        if self.rect is None:
            return  # No movement if rect is invalid

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
        """Draws the enemy with a black outline and a flashing hit effect."""
        if self.rect is None:
            return  # Don't draw if the enemy is removed

        current_time = pygame.time.get_ticks()
        outline_color = (0, 0, 0)  # Default black outline
        base_color = (255, 0, 0)  # Normal red enemy

        # Damage effect
        if current_time - self.hit_timer < self.hit_effect_duration:
            enemy_color = (255, 255, 255)  # White flash
            outline_color = (255, 0, 0)  # Red outline on hit
        elif self.is_dying:
            enemy_color = (255, 255, 255)  # White flash on death
        else:
            enemy_color = base_color

        # Shrink slightly when dying
        shrink_factor = 0.75 if self.is_dying else 1.0
        width, height = int(self.rect.width * shrink_factor), int(self.rect.height * shrink_factor)
        draw_x = self.rect.x - camera_x + (self.rect.width - width) // 2
        draw_y = self.rect.y - camera_y + (self.rect.height - height) // 2

        # Draw outline
        pygame.draw.rect(screen, outline_color,
                         pygame.Rect(draw_x - 3, draw_y - 3, width + 6, height + 6))

        # Draw enemy
        pygame.draw.rect(screen, enemy_color, pygame.Rect(draw_x, draw_y, width, height))

        # Draw health bar
        if not self.is_dying:
            self.draw_health_bar(screen, camera_x, camera_y, enemy_color)

    def draw_health_bar(self, screen, camera_x, camera_y, color):
        """Draws a health bar above the enemy."""
        if self.health > 0:
            health_bar_width = int((self.health / self.max_health) * self.rect.width)
            pygame.draw.rect(screen, (0, 255, 0),  # Green health bar
                             pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y - 5, health_bar_width, 3))

class FastEnemy(Enemy):
    """Smaller, faster enemy with 1 HP."""
    def __init__(self, x, y):
        super().__init__(x, y, 2)  # Fast enemies have 2 HP
        self.rect = pygame.Rect(x, y, 30, 30)  # Smaller size
        self.speed = ENEMY_SPEED * 1.8  # Faster speed

    # Yellow Enemy (Fast)
    def draw(self, screen, camera_x, camera_y):
        """Draws the fast enemy with a black outline and hit effect."""
        current_time = pygame.time.get_ticks()
        outline_color = (0, 0, 0)
        base_color = (255, 255, 0)

        if current_time - self.hit_timer < self.hit_effect_duration:
            enemy_color = (255, 255, 255)
            outline_color = (255, 0, 0)  # Flash red outline when hit
        else:
            enemy_color = base_color

        pygame.draw.rect(screen, outline_color,
                         pygame.Rect(self.rect.x - camera_x - 3, self.rect.y - camera_y - 3,
                                     self.rect.width + 6, self.rect.height + 6))

        pygame.draw.rect(screen, enemy_color, pygame.Rect(
            self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height
        ))

        self.draw_health_bar(screen, camera_x, camera_y, enemy_color)


class TankEnemy(Enemy):
    """Bigger, slower enemy with 5 HP."""
    def __init__(self, x, y):
        super().__init__(x, y, 8)  # Tank enemies have 8 HP
        self.rect = pygame.Rect(x, y, 50, 50)  # Bigger size
        self.speed = ENEMY_SPEED * 0.75  # Slower movement

    def draw(self, screen, camera_x, camera_y):
        """Draws the tank enemy with a black outline and hit effect."""
        current_time = pygame.time.get_ticks()
        outline_color = (0, 0, 0)
        base_color = (0, 0, 225)

        if current_time - self.hit_timer < self.hit_effect_duration:
            enemy_color = (255, 255, 255)
            outline_color = (255, 0, 0)  # Flash red outline when hit
        else:
            enemy_color = base_color

        pygame.draw.rect(screen, outline_color,
                         pygame.Rect(self.rect.x - camera_x - 3, self.rect.y - camera_y - 3,
                                     self.rect.width + 6, self.rect.height + 6))

        pygame.draw.rect(screen, enemy_color, pygame.Rect(
            self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height
        ))

        self.draw_health_bar(screen, camera_x, camera_y, enemy_color)

class DasherEnemy(Enemy):
    """Enemy that dashes when close to the player."""
    def __init__(self, x, y):
        super().__init__(x, y, 4)  # 4 HP
        self.rect = pygame.Rect(x, y, 35, 35)  # Slightly smaller hitbox
        self.base_speed = ENEMY_SPEED * 1  # Normal movement speed
        self.dash_speed = ENEMY_SPEED * 25  # Much faster dash speed
        self.speed = self.base_speed
        self.dash_cooldown = 2000  # 2-second cooldown between dashes
        self.charge_time = 500  # 0.5-second warning before dashing
        self.last_dash_time = pygame.time.get_ticks()
        self.is_charging = False
        self.charge_start_time = 0

    def update(self, player, obstacles, game):
        """Updates movement, initiating a charge-up visual before dashing."""
        current_time = pygame.time.get_ticks()
        distance_to_player = math.sqrt((player.rect.centerx - self.rect.centerx) ** 2 + (player.rect.centery - self.rect.centery) ** 2)

        if self.is_dying:
            # ✅ Remove enemy if death effect is finished
            if pygame.time.get_ticks() - self.death_timer > 100:  # Adjust delay as needed
                print(f"💀 Enemy removed at {self.rect.topleft}")
                game.enemies.remove(self)  # ✅ Now actually removes the enemy
            return  # ✅ Prevents further updates

        if self.rect is None:
            return  # No movement if rect is invalid

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
        """Draws the dasher enemy with a black outline and a distinct charge effect."""
        if self.rect is None:
            return  # Don't draw if removed

        current_time = pygame.time.get_ticks()
        outline_color = (0, 0, 0)
        base_color = (255, 100, 100)  # Default pinkish-red

        # Damage & charge effect
        if current_time - self.hit_timer < self.hit_effect_duration:
            enemy_color = (255, 255, 255)  # White flash on hit
            outline_color = (255, 0, 0)  # Flash red outline when hit
        elif self.is_charging:
            enemy_color = (220, 50, 120)  # **NEW CHARGE COLOR** (Deep pink/magenta)
        elif self.is_dying:
            enemy_color = (255, 255, 255)  # White flash on death
            outline_color = (255, 0, 0)

            if current_time - self.death_timer > self.death_effect_duration:
                self.rect = None
                return
        else:
            enemy_color = base_color

        pygame.draw.rect(screen, outline_color,
                         pygame.Rect(self.rect.x - camera_x - 3, self.rect.y - camera_y - 3,
                                     self.rect.width + 6, self.rect.height + 6))

        pygame.draw.rect(screen, enemy_color,
                         pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y,
                                     self.rect.width, self.rect.height))

        self.draw_health_bar(screen, camera_x, camera_y, enemy_color)

class ShooterEnemy(Enemy):
    """An enemy that moves into range, stops, and shoots bullets at the player."""
    def __init__(self, x, y):
        super().__init__(x, y, 4)  # 4 HP
        self.rect = pygame.Rect(x, y, 35, 35)  # Slightly smaller than normal enemies
        self.attack_range = 300  # Stops moving when within 300 pixels of player
        self.shoot_cooldown = 2000  # Fires every 2 seconds
        self.last_shot_time = pygame.time.get_ticks()  # Track last shot time
        self.speed = ENEMY_SPEED * 0.8  # Moves slightly slower than normal enemies
        self.is_shooting = False  # Indicates if preparing to shoot
        self.shoot_warning_time = 500  # Time before actually firing after warning

    def update(self, player, obstacles, enemy_bullets):
        """Updates movement and shooting behavior."""
        current_time = pygame.time.get_ticks()
        distance_to_player = math.sqrt(
            (player.rect.centerx - self.rect.centerx) ** 2 +
            (player.rect.centery - self.rect.centery) ** 2
        )

        if self.is_dying:
            # ✅ Remove enemy if death effect is finished
            if pygame.time.get_ticks() - self.death_timer > 100:  # Adjust delay as needed
                print(f"💀 Enemy removed at {self.rect.topleft}")
                game.enemies.remove(self)  # ✅ Now actually removes the enemy
            return  # ✅ Prevents further updates

        if self.rect is None:
            return  # No movement if rect is invalid

        if self.is_shooting:
            # Check if the warning period has passed, then fire
            if current_time - self.shoot_start_time >= self.shoot_warning_time:
                self.fire(player, enemy_bullets)
            return  # Stay in shooting state until the bullet fires

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
            # If within range, stop and prepare to shoot
            if current_time - self.last_shot_time > self.shoot_cooldown:
                self.is_shooting = True  # Enable warning color
                self.shoot_start_time = current_time  # Track when warning starts

    def fire(self, player, enemy_bullets):
        """Shoots a bullet at the player after the pre-fire warning."""
        from shooterbullet import ShooterBullet  # ✅ Fix circular import

        self.is_shooting = False  # ✅ Reset shooting state so it can shoot again
        self.last_shot_time = pygame.time.get_ticks()  # ✅ Reset cooldown timer
        enemy_bullets.append(ShooterBullet(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery))

    def draw(self, screen, camera_x, camera_y):
        """Draws the shooter enemy with a black outline and a visual cue before firing."""
        if self.rect is None:
            return  # Don't draw if removed

        current_time = pygame.time.get_ticks()
        outline_color = (0, 0, 0)  # Default black outline
        base_color = (150, 0, 255)  # Default purple

        # Damage, pre-fire, and death effects
        if current_time - self.hit_timer < self.hit_effect_duration:
            enemy_color = (255, 255, 255)  # White flash when hit
            outline_color = (255, 0, 0)  # Flash red outline when hit
        elif self.is_shooting:
            enemy_color = (255, 0, 200)   # **New Pre-Fire Warning Color (# Brighter, higher contrast purple)**
        elif self.is_dying:
            enemy_color = (255, 255, 255)  # White flash on death
            outline_color = (255, 0, 0)

            # Ensure death animation plays before removing enemy
            if current_time - self.death_timer > self.death_effect_duration:
                self.rect = None
                return
        else:
            enemy_color = base_color

        # Draw outline first
        pygame.draw.rect(screen, outline_color,
                         pygame.Rect(self.rect.x - camera_x - 3, self.rect.y - camera_y - 3,
                                     self.rect.width + 6, self.rect.height + 6))

        # Draw enemy
        pygame.draw.rect(screen, enemy_color,
                         pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y,
                                     self.rect.width, self.rect.height))

        self.draw_health_bar(screen, camera_x, camera_y, enemy_color)

class SwarmEnemy(Enemy):
    """A weak, fast-moving enemy that spawns in groups and maintains swarm behavior."""
    def __init__(self, x, y, swarm_group):
        super().__init__(x, y, 1)  # 1 HP
        self.rect = pygame.Rect(x, y, 25, 25)  # Smaller than regular enemies
        self.speed = ENEMY_SPEED * 1.5  # Faster movement
        self.swarm_group = swarm_group  # Reference to the swarm
        self.swarm_separation_distance = 30  # Min distance to avoid stacking
        self.swarm_cohesion_strength = 0.02  # Strength of movement toward swarm center
        self.swarm_alignment_strength = 0.1  # Strength of moving in similar direction

    def update(self, player, obstacles, game):
        """Moves toward the player while maintaining swarm behavior."""

        if self.is_dying:
            # ✅ Remove enemy if death effect is finished
            if pygame.time.get_ticks() - self.death_timer > 100:  # Adjust delay as needed
                print(f"💀 Enemy removed at {self.rect.topleft}")
                game.enemies.remove(self)  # ✅ Now actually removes the enemy
            return  # ✅ Prevents further updates

        if self.rect is None:
            return  # No movement if rect is invalid

        # Get direction toward player
        dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)

        move_x = self.speed * math.cos(angle)
        move_y = self.speed * math.sin(angle)

        # Swarm Cohesion: Move toward the center of the swarm
        if self.swarm_group:
            swarm_center_x = sum(enemy.rect.centerx for enemy in self.swarm_group) / len(self.swarm_group)
            swarm_center_y = sum(enemy.rect.centery for enemy in self.swarm_group) / len(self.swarm_group)
            move_x += (swarm_center_x - self.rect.centerx) * self.swarm_cohesion_strength
            move_y += (swarm_center_y - self.rect.centery) * self.swarm_cohesion_strength

        # Swarm Separation: Avoid stacking with other swarm members
        for other in self.swarm_group:
            if other != self:
                distance = math.sqrt((self.rect.centerx - other.rect.centerx) ** 2 +
                                     (self.rect.centery - other.rect.centery) ** 2)
                if distance < self.swarm_separation_distance:
                    move_x += (self.rect.centerx - other.rect.centerx) * 0.05
                    move_y += (self.rect.centery - other.rect.centery) * 0.05

        # Swarm Alignment: Move in the general direction of the swarm
        avg_velocity_x = sum(enemy.speed * math.cos(angle) for enemy in self.swarm_group) / len(self.swarm_group)
        avg_velocity_y = sum(enemy.speed * math.sin(angle) for enemy in self.swarm_group) / len(self.swarm_group)
        move_x += avg_velocity_x * self.swarm_alignment_strength
        move_y += avg_velocity_y * self.swarm_alignment_strength

        # Collision Handling
        old_x, old_y = self.rect.x, self.rect.y
        self.rect.x += move_x
        if any(obstacle.collides(self.rect) for obstacle in obstacles):
            self.rect.x = old_x

        self.rect.y += move_y
        if any(obstacle.collides(self.rect) for obstacle in obstacles):
            self.rect.y = old_y

    def draw(self, screen, camera_x, camera_y):
        """Draws the swarm enemy with a black outline and sickly green color."""
        current_time = pygame.time.get_ticks()
        outline_color = (0, 0, 0)  # Black outline
        base_color = (100, 255, 100)  # Sickly green

        # Flash effect when hit
        if current_time - self.hit_timer < self.hit_effect_duration:
            enemy_color = (255, 255, 255)  # Flash white
            outline_color = (255, 0, 0)  # Red outline when hit
        else:
            enemy_color = base_color

        pygame.draw.rect(screen, outline_color,
                         pygame.Rect(self.rect.x - camera_x - 3, self.rect.y - camera_y - 3,
                                     self.rect.width + 6, self.rect.height + 6))

        pygame.draw.rect(screen, enemy_color, pygame.Rect(
            self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height
        ))

        self.draw_health_bar(screen, camera_x, camera_y, enemy_color)


class DeathAnimation:
    """Handles the death animation effect."""
    def __init__(self, x, y, size=40, duration=500):
        self.rect = pygame.Rect(x, y, size, size)  # Same size as enemy
        self.start_time = pygame.time.get_ticks()  # Track when animation starts
        self.duration = duration  # How long the effect lasts in ms
        self.alpha = 255  # Opacity for fade effect

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


