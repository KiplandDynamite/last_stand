import pygame
import math

class ShooterBullet:
    """A bullet fired by enemies that moves in a straight line and damages the player."""
    BULLET_SPEED = 7  # Slightly slower than player bullets

    def __init__(self, x, y, target_x, target_y):
        self.rect = pygame.Rect(x, y, 8, 8)
        angle = math.atan2(target_y - y, target_x - x)
        self.speed_x = self.BULLET_SPEED * math.cos(angle)
        self.speed_y = self.BULLET_SPEED * math.sin(angle)

    def update(self, player, obstacles, enemy_bullets):
        """Moves the bullet and checks for collisions."""
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Check collision with player
        if self.rect.colliderect(player.rect):
            player.take_damage()
            enemy_bullets.remove(self)
            return

        # Check collision with obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                enemy_bullets.remove(self)
                return

    def draw(self, screen, camera_x, camera_y):
        """Draws the enemy bullet."""
        pygame.draw.rect(
            screen,
            (222, 10, 10),
            pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height)
        )
