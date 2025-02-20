import pygame
import random

class CurrencyPickup:
    """Represents a dropped currency item on the gameboard."""
    def __init__(self, x, y, amount):
        self.rect = pygame.Rect(x, y, 15, 15)  # Small collectible
        self.amount = amount
        self.color = (255, 223, 0)  # Gold color for visibility

    def draw(self, screen, camera_x, camera_y):
        """Draws the currency pickup as a silver coin with a black border."""
        screen_x = self.rect.x - camera_x + 7
        screen_y = self.rect.y - camera_y + 7

        # Black outline
        pygame.draw.circle(screen, (0, 0, 0), (screen_x, screen_y), 8)

        # Silver coin
        pygame.draw.circle(screen, (192, 192, 192), (screen_x, screen_y), 7)

    def check_pickup(self, player):
        """Check if the player touches the currency, and collect it."""
        if self.rect.colliderect(player.rect):
            player.currency += self.amount
            return True  # Flag for removal
        return False
