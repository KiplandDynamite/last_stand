import pygame
import math
from enemy import Enemy, FastEnemy, TankEnemy, DeathAnimation

BULLET_SPEED = 10
BORDER_THICKNESS = 10  # Matches the border thickness

class Bullet:
    def __init__(self, x, y, angle, map_width, map_height):
        self.rect = pygame.Rect(x, y, 10, 10)
        self.speed_x = BULLET_SPEED * math.cos(angle)
        self.speed_y = BULLET_SPEED * math.sin(angle)
        self.MAP_WIDTH = map_width
        self.MAP_HEIGHT = map_height

    def update(self, obstacles, enemies, game):
        """Moves bullet and checks for collisions"""

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Check if bullet hits the border and remove it
        if (self.rect.x <= 0 or self.rect.x >= self.MAP_WIDTH or
                self.rect.y <= 0 or self.rect.y >= self.MAP_HEIGHT):
            if self in game.player.bullets:
                game.player.bullets.remove(self)
            return

        # Check collision with obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if self in game.player.bullets:
                    game.player.bullets.remove(self)
                return

        # Check collision with enemies
        for enemy in enemies:

            if enemy.rect is not None and self.rect.colliderect(enemy.rect):

                enemy_died = enemy.take_damage()  # Check if enemy is dead

                if self in game.player.bullets:
                    game.player.bullets.remove(self)  # Remove bullet on hit

                if enemy_died:
                    game.death_animations.append(DeathAnimation(enemy.rect.x, enemy.rect.y, enemy.rect.width))
                    enemies.remove(enemy)  # Remove enemy immediately
                    game.score += 50  # Default score for normal enemies

                    # Score scaling for different enemies
                    if isinstance(enemy, FastEnemy):
                        game.score += 75
                    elif isinstance(enemy, TankEnemy):
                        game.score += 200

                    print(f"Updated Score: {game.score}")  # Debugging

    def draw(self, screen, camera_x, camera_y):
        """Draws the bullet, accounting for camera offset"""
        pygame.draw.rect(screen, (255, 255, 0),
                         pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height))
