import pygame

class ExplosionEffect:
    """Handles a visual explosion effect."""
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius
        self.start_time = pygame.time.get_ticks()  # Track explosion start time

    def draw(self, screen, camera_x, camera_y):
        """Draws a fading explosion effect."""
        time_elapsed = pygame.time.get_ticks() - self.start_time

        if time_elapsed < 300:  # Explosion lasts for 300ms
            alpha = max(255 - (time_elapsed * 2), 0)  # Fade effect
            explosion_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, (255, 140, 0, alpha), (self.radius, self.radius), self.radius)
            screen.blit(explosion_surface, (self.position[0] - camera_x - self.radius, self.position[1] - camera_y - self.radius))
        return time_elapsed >= 300  # Return True when animation ends
