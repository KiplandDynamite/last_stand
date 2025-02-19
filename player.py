import pygame
import math
from bullet import Bullet

PLAYER_SPEED = 5
BORDER_THICKNESS = 10  # Matches the visual border thickness


class Player:
    def __init__(self, x, y, map_width, map_height):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.health = 3
        self.bullets = []
        self.MAP_WIDTH = map_width
        self.MAP_HEIGHT = map_height
        # Optional: you can adjust how often the player takes damage
        # from an obstacle (in milliseconds). We'll handle that in the Game class.

    def update(self, obstacles):
        keys = pygame.key.get_pressed()

        move_x, move_y = 0, 0
        if keys[pygame.K_w]: move_y -= PLAYER_SPEED
        if keys[pygame.K_s]: move_y += PLAYER_SPEED
        if keys[pygame.K_a]: move_x -= PLAYER_SPEED
        if keys[pygame.K_d]: move_x += PLAYER_SPEED

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
        """Shoots a bullet towards the mouse location."""
        angle = math.atan2(
            mouse_y - self.rect.centery,
            mouse_x - self.rect.centerx
        )
        bullet = Bullet(self.rect.centerx, self.rect.centery, angle, self.MAP_WIDTH, self.MAP_HEIGHT)
        self.bullets.append(bullet)

    def take_damage(self):
        """Reduces health on collision with enemies or obstacles."""
        self.health -= 1

    def draw(self, screen, camera_x, camera_y):
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            pygame.Rect(
                self.rect.x - camera_x,
                self.rect.y - camera_y,
                self.rect.width,
                self.rect.height
            )
        )
