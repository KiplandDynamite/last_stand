import pygame
import math
from enemy import Enemy, FastEnemy, TankEnemy, DasherEnemy, ShooterEnemy, DeathAnimation

BULLET_SPEED = 10
BORDER_THICKNESS = 10  # Matches the border thickness
TRAVEL_DISTANCE_AFTER_HIT = 5

class Bullet:
    def __init__(self, x, y, angle, map_width, map_height, pierce=0, delay=0):
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

    def fire(self):
        """Activates bullet movement."""
        self.fired = True

    def update(self, obstacles, enemies, game):
        """Moves the bullet and handles collisions only if it has been fired."""
        current_time = pygame.time.get_ticks()
        if current_time < self.fire_time:
            return  # ✅ Delayed bullet waiting to fire

        if not self.fired:
            self.fire()  # ✅ Activate bullet movement

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y


        # Remove bullet if it leaves the map boundaries
        if not (0 <= self.rect.x <= self.MAP_WIDTH and 0 <= self.rect.y <= self.MAP_HEIGHT):
            if self in game.player.bullets:
                game.player.bullets.remove(self)
            return

        # Check for collision with obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if self in game.player.bullets:
                    game.player.bullets.remove(self)
                return

        # Track enemies hit (to prevent multiple hits in one update cycle)
        enemies_hit = []

        # Check for collisions with enemies
        for enemy in enemies[:]:
            if enemy.rect is not None and self.rect.colliderect(enemy.rect):
                if enemy in enemies_hit:  # ✅ Prevent hitting the same enemy twice in one update cycle
                    continue

                enemies_hit.append(enemy)  # ✅ Register enemy as "hit" to prevent multiple hits in one update

                # Deal full damage to enemy
                enemy_died = enemy.take_damage(self.damage)

                if enemy_died:
                    game.death_animations.append(DeathAnimation(enemy.rect.x, enemy.rect.y, enemy.rect.width))
                    enemies.remove(enemy)

                    # Score scaling for different enemies
                    if isinstance(enemy, FastEnemy):
                        game.score += 75
                        game.player.gain_xp(2, game)
                    elif isinstance(enemy, TankEnemy):
                        game.score += 200
                        game.player.gain_xp(4, game)
                    elif isinstance(enemy, DasherEnemy):
                        game.score += 100
                        game.player.gain_xp(6, game)
                    elif isinstance(enemy, ShooterEnemy):
                        game.score += 100
                        game.player.gain_xp(7, game)
                    else:
                        game.score += 50
                        game.player.gain_xp(1, game)

                # ✅ Reduce pierce count after hitting an enemy
                self.pierce -= 1

                # ✅ Move bullet forward slightly before it can hit another enemy
                self.rect.x += self.speed_x * TRAVEL_DISTANCE_AFTER_HIT
                self.rect.y += self.speed_y * TRAVEL_DISTANCE_AFTER_HIT

                # ✅ If bullet has no more pierce left, remove it
                if self.pierce < 0:
                    if self in game.player.bullets:
                        game.player.bullets.remove(self)
                    return

        # ✅ Ensure bullet color updates correctly
        self.update_bullet_color()

    def draw(self, screen, camera_x, camera_y):
        """Draws the bullet, changing color based on pierce level."""
        # Color changes based on pierce level
        if self.pierce == 0:
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
