import pygame
import math
import random
from enemy import Enemy, FastEnemy, TankEnemy, DasherEnemy, ShooterEnemy, DeathAnimation, SwarmEnemy
from currency import CurrencyPickup
from effects import ExplosionEffect

BULLET_SPEED = 10
BORDER_THICKNESS = 10  # Matches the border thickness
TRAVEL_DISTANCE_AFTER_HIT = 5

class Bullet:
    def __init__(self, x, y, angle, map_width, map_height, pierce=0, delay=0, ricochet_count=0, explosive=False):
        """Initializes a bullet with movement, piercing ability, and a fire delay."""
        self.rect = pygame.Rect(x, y, 10, 10)
        self.speed_x = BULLET_SPEED * math.cos(angle)
        self.speed_y = BULLET_SPEED * math.sin(angle)
        self.MAP_WIDTH = map_width
        self.MAP_HEIGHT = map_height
        self.pierce = pierce
        self.damage = 1  # ✅ Piercing hits multiple enemies
        self.fired = False  # ✅ Prevents bullets from moving before firing
        self.fire_time = pygame.time.get_ticks() + delay  # ✅ Sets fire time
        self.ricochet_count = ricochet_count
        self.explosive = explosive
        self.active = True

    def fire(self):
        """Activates bullet movement."""
        self.fired = True

    def update(self, obstacles, enemies, game):
        """Moves the bullet and handles collisions with walls, obstacles, and enemies."""
        current_time = pygame.time.get_ticks()
        if current_time < self.fire_time:
            return  # ✅ Delayed bullet waiting to fire

        if not self.fired:
            self.fire()  # ✅ Activate bullet movement

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # ✅ Check for obstacle (wall) collisions FIRST
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if self.ricochet_count > 0:
                    self.ricochet_count -= 1

                    # ✅ Determine if collision was horizontal or vertical
                    overlap_x = min(abs(self.rect.right - obstacle.rect.left),
                                    abs(self.rect.left - obstacle.rect.right))
                    overlap_y = min(abs(self.rect.bottom - obstacle.rect.top),
                                    abs(self.rect.top - obstacle.rect.bottom))

                    if overlap_x < overlap_y:
                        self.speed_x = -self.speed_x  # ✅ Flip horizontally
                        self.rect.x += self.speed_x * 3  # ✅ Prevent sticking
                    else:
                        self.speed_y = -self.speed_y  # ✅ Flip vertically
                        self.rect.y += self.speed_y * 3  # ✅ Prevent sticking

                    break  # ✅ Prevent multiple ricochets in one frame
                else:
                    # ✅ Remove bullet if out of ricochets
                    if self in game.player.bullets:
                        game.player.bullets.remove(self)
                    return

                    # ✅ Check for Screen Border Collisions (AFTER obstacles)
        if self.rect.top <= 0 or self.rect.bottom >= self.MAP_HEIGHT:
            if self.ricochet_count > 0:
                self.ricochet_count -= 1
                self.speed_y = -self.speed_y  # ✅ Flip only the vertical component
                self.rect.y += self.speed_y  # ✅ Prevents sticking
            else:
                if self in game.player.bullets:
                    game.player.bullets.remove(self)
                return

        if self.rect.left <= 0 or self.rect.right >= self.MAP_WIDTH:
            if self.ricochet_count > 0:
                self.ricochet_count -= 1
                self.speed_x = -self.speed_x  # ✅ Flip only the horizontal component
                self.rect.x += self.speed_x  # ✅ Prevents sticking
            else:
                if self in game.player.bullets:
                    game.player.bullets.remove(self)
                return

                # ✅ If bullet goes out of bounds, remove it
        if not (0 <= self.rect.x <= self.MAP_WIDTH and 0 <= self.rect.y <= self.MAP_HEIGHT):
            if self in game.player.bullets:
                game.player.bullets.remove(self)
            return

            # ✅ Track enemies hit (prevents multiple hits in one update)
        enemies_hit = []

        # ✅ Check for collisions with enemies
        for enemy in enemies[:]:
            if enemy.rect is not None and self.rect.colliderect(enemy.rect):
                if enemy in enemies_hit:
                    continue  # ✅ Prevent hitting the same enemy twice in one update cycle

                enemies_hit.append(enemy)

                if isinstance(enemy, Enemy):  # Ensure it's an actual enemy, not a Missile
                    enemy_died = enemy.take_damage(self.damage)
                else:
                    enemy_died = False  # Ensure enemy_died is always defined

                if self.explosive:
                    explosion_radius = 50
                    explosion_center = (self.rect.centerx, self.rect.centery)
                    game.explosions.append(ExplosionEffect(explosion_center, explosion_radius))

                    # ✅ Damage nearby enemies
                    for other_enemy in enemies[:]:
                        if math.dist(explosion_center,
                                     (other_enemy.rect.centerx, other_enemy.rect.centery)) < explosion_radius:
                            other_enemy.take_damage()

                if enemy_died:
                    game.death_animations.append(DeathAnimation(enemy.rect.x, enemy.rect.y, enemy.rect.width))
                    enemies.remove(enemy)

                    # ✅ Handle XP & Score Rewards
                    if isinstance(enemy, FastEnemy):
                        game.score += 75
                        game.player.gain_xp(4, game)
                        drop_chance = 0.3
                        currency_amount = random.randint(1, 3)
                    elif isinstance(enemy, TankEnemy):
                        game.score += 200
                        game.player.gain_xp(8, game)
                        drop_chance = 0.7
                        currency_amount = random.randint(3, 7)
                    elif isinstance(enemy, DasherEnemy):
                        game.score += 100
                        game.player.gain_xp(12, game)
                        drop_chance = 0.5
                        currency_amount = random.randint(2, 5)
                    elif isinstance(enemy, ShooterEnemy):
                        game.score += 100
                        game.player.gain_xp(14, game)
                        drop_chance = 0.5
                        currency_amount = random.randint(2, 4)
                    elif isinstance(enemy, SwarmEnemy):
                        game.score += 5
                        game.player.gain_xp(2, game)
                        drop_chance = 0.2
                        currency_amount = 1
                    else:
                        game.score += 50
                        game.player.gain_xp(3, game)
                        drop_chance = 0.4
                        currency_amount = random.randint(1, 2)

                    # ✅ Drop Currency with Random Chance
                    if random.random() < drop_chance:
                        currency_pickup = CurrencyPickup(enemy.rect.centerx, enemy.rect.centery, currency_amount)
                        game.currency_drops.append(currency_pickup)

                # ✅ Reduce pierce count after hitting an enemy
                self.pierce -= 1

                # ✅ Move bullet forward slightly before it can hit another enemy
                self.rect.x += self.speed_x * TRAVEL_DISTANCE_AFTER_HIT
                self.rect.y += self.speed_y * TRAVEL_DISTANCE_AFTER_HIT

                if self.pierce < 0:  # ✅ Remove bullet if pierce is depleted
                    if self in game.player.bullets:
                        game.player.bullets.remove(self)
                    return

                    # ✅ Ensure bullet color updates correctly
        self.update_bullet_color()

    def draw(self, screen, camera_x, camera_y):
        """Draws the bullet, changing color based on pierce level."""
        # Color changes based on pierce level
        if self.explosive:
            color = (153,76,0)
        elif self.pierce == 0:
            color = (255, 255, 0)  # Yellow (default)
        elif self.pierce == 1:
            color = (255, 165, 0)  # Orange (piercing level 1)
        elif self.pierce == 2:
            color = (255, 69, 0)  # Red-orange (piercing level 2)
        else:
            color = (255, 0, 0)  # Red (high piercing level)

        pygame.draw.rect(screen, color,
                         pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height))

    def update_bullet_color(self):
        """Updates bullet color based on remaining damage and pierce level."""
        if self.damage <= 1:
            color = (255, 255, 0)  # Yellow (base bullet)
        elif self.damage == 2:
            color = (255, 165, 0)  # Orange (mid-tier damage)
        elif self.damage == 3:
            color = (255, 69, 0)  # Red-orange (higher damage)
        else:
            color = (255, 0, 0)  # Red (max damage)

        self.color = color  # ✅ Ensure the color updates dynamically

    class ExplosionEffect:
        """Handles a visual explosion effect."""

        def __init__(self, position, radius):
            self.position = position
            self.radius = radius
            self.start_time = pygame.time.get_ticks()  # Track when explosion starts

        def draw(self, screen, camera_x, camera_y):
            """Draws an expanding explosion effect."""
            time_elapsed = pygame.time.get_ticks() - self.start_time

            if time_elapsed < 300:  # Explosion lasts for 300ms
                alpha = max(255 - (time_elapsed * 2), 0)  # Fade out effect
                explosion_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(explosion_surface, (255, 140, 0, alpha), (self.radius, self.radius), self.radius)
                screen.blit(explosion_surface,
                            (self.position[0] - camera_x - self.radius, self.position[1] - camera_y - self.radius))
            return time_elapsed >= 300  # Signal removal after 300ms

