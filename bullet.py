import pygame
import math
from enemy import Enemy, FastEnemy, TankEnemy, DasherEnemy, ShooterEnemy, DeathAnimation

BULLET_SPEED = 10
BORDER_THICKNESS = 10  # Matches the border thickness

class Bullet:
    def __init__(self, x, y, angle, map_width, map_height, pierce=0, delay=0):
        """Initializes a bullet with movement, piercing ability, and a fire delay."""
        self.rect = pygame.Rect(x, y, 10, 10)
        self.speed_x = BULLET_SPEED * math.cos(angle)
        self.speed_y = BULLET_SPEED * math.sin(angle)
        self.MAP_WIDTH = map_width
        self.MAP_HEIGHT = map_height
        self.pierce = pierce
        self.damage = 1 + pierce  # ✅ Piercing increases bullet damage
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

        # Track enemies hit (for piercing)
        enemies_hit = []

        # Check for collisions with enemies
        for enemy in enemies[:]:
            if enemy.rect is not None and self.rect.colliderect(enemy.rect):
                enemy_died = enemy.take_damage(self.damage)
                enemies_hit.append(enemy)

                if enemy_died:
                    game.death_animations.append(DeathAnimation(enemy.rect.x, enemy.rect.y, enemy.rect.width))
                    enemies.remove(enemy)
                    game.score += 50
                    game.player.gain_xp(25, game)

                    # Score scaling for different enemies
                    if isinstance(enemy, FastEnemy):
                        game.score += 75
                    elif isinstance(enemy, TankEnemy):
                        game.score += 200
                    elif isinstance(enemy, DasherEnemy):
                        game.score += 100
                    elif isinstance(enemy, ShooterEnemy):
                        game.score += 100

                    # ✅ Debugging: Confirm bullet hit enemy
                    print(f"💥 Bullet hit enemy at {enemy.rect.x}, {enemy.rect.y}, Damage: {self.damage}")

                # ✅ Handle piercing bullets
                if self.pierce <= 0:
                    if self in game.player.bullets:
                        game.player.bullets.remove(self)
                    return
                else:
                    self.pierce -= 1  # ✅ Reduce pierce count but keep bullet active

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
