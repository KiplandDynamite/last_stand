import pygame
import math

ENEMY_SPEED = 2  # Base enemy speed

class Enemy:
    """Base enemy class with HP system."""
    def __init__(self, x, y, health):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = ENEMY_SPEED
        self.health = health
        self.max_health = health  # Store max HP for health bar calculations

    def take_damage(self):
        """Reduces HP when hit. Returns True if HP reaches zero."""
        self.health -= 1
        print(f"Enemy at {self.rect.topleft} took damage! HP left: {self.health}")  # Debugging

        return self.health <= 0  # Only return True if the enemy should be removed

    def update(self, player, obstacles):
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
        pygame.draw.rect(
            screen,
            (255, 0, 0),  # Red for normal enemies
            pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height)
        )

        # Draw health bar
        self.draw_health_bar(screen, camera_x, camera_y, (255, 0, 0))

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
        pygame.draw.rect(
            screen,
            (255, 255, 0),  # Yellow for fast enemies
            pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height)
        )

        # Draw health bar
        self.draw_health_bar(screen, camera_x, camera_y, (255, 255, 0))


class TankEnemy(Enemy):
    """Bigger, slower enemy with 5 HP."""
    def __init__(self, x, y):
        super().__init__(x, y, 5)  # Tank enemies have 5 HP
        self.rect = pygame.Rect(x, y, 50, 50)  # Bigger size
        self.speed = ENEMY_SPEED * 0.75  # Slower movement

    def draw(self, screen, camera_x, camera_y):
        pygame.draw.rect(
            screen,
            (0, 0, 255),  # Blue for tank enemies
            pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height)
        )

        # Draw health bar
        self.draw_health_bar(screen, camera_x, camera_y, (0, 0, 255))
