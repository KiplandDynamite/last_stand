import pygame
import math
from enemy import Enemy
from effects import ExplosionEffect


class Missile:
    """ A homing missile fired by the Boss that slowly tracks the player and explodes on wall impact. """
    SPEED = 3  # Base missile speed
    TURN_RATE = 0.05  # How quickly the missile turns toward the player
    EXPLOSION_RADIUS = 50  # Damage area on explosion

    def __init__(self, x, y, target):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.target = target
        dx, dy = target.rect.centerx - x, target.rect.centery - y
        self.angle = math.atan2(dy, dx)  # Initial trajectory
        self.speed_x = self.SPEED * math.cos(self.angle)
        self.speed_y = self.SPEED * math.sin(self.angle)

    def update(self, player, obstacles, game):
        """ Moves the missile, adjusts direction toward the player, and handles collisions. """
        # Homing logic - gradually adjust trajectory
        dx, dy = self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery
        target_angle = math.atan2(dy, dx)

        # Gradually turn towards the target
        self.angle += (target_angle - self.angle) * self.TURN_RATE
        self.speed_x = self.SPEED * math.cos(self.angle)
        self.speed_y = self.SPEED * math.sin(self.angle)

        # Move the missile
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Check for wall collision
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                self.explode(game)
                return

    def explode(self, game):
        """ Handles missile explosion, creating a visual effect and damaging nearby enemies. """
        game.explosions.append(ExplosionEffect((self.rect.centerx, self.rect.centery), self.EXPLOSION_RADIUS))
        for enemy in game.enemies:
            if isinstance(enemy, Enemy):  # Ensure we only damage valid enemies
                distance = math.sqrt(
                    (enemy.rect.centerx - self.rect.centerx) ** 2 + (enemy.rect.centery - self.rect.centery) ** 2)
                if distance <= self.EXPLOSION_RADIUS:
                    enemy.take_damage(2)  # Deals 2 damage to nearby enemies
        game.enemies.remove(self)  # Remove missile after explosion

    def draw(self, screen, camera_x, camera_y):
        """ Draws the missile as a red rectangle with a black outline. """
        pygame.draw.rect(screen, (0, 0, 0),
                         pygame.Rect(self.rect.x - camera_x - 2, self.rect.y - camera_y - 2, 20, 20))  # Outline
        pygame.draw.rect(screen, (255, 50, 50),
                         pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y, 16, 16))  # Missile
