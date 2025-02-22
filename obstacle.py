import pygame
import random
import math

MAP_WIDTH, MAP_HEIGHT = 1600, 1200
BORDER_THICKNESS = 10
NUM_OBSTACLES = 10  # Adjust for difficulty


class Obstacle:
    def __init__(self, shape, x, y, width, height=None):
        """Initialize an obstacle with a specific shape."""
        self.shape = shape
        self.x = x
        self.y = y
        self.width = width
        self.height = height if height else width  # Circles use width as diameter
        if self.shape in ["square", "rectangle"]:
            # Rectangular collision box
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        elif self.shape == "circle":
            # Circular collision: store a bounding rect + radius
            self.radius = self.width // 2
            # For circles, (x, y) is the top-left of the bounding square
            self.rect = pygame.Rect(self.x, self.y, self.width, self.width)

    def draw(self, screen, camera_x, camera_y):
        """Draws the obstacle as a rectangular house with a center beam and a border."""
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        if self.shape in ["square", "rectangle"]:
            # 🎨 **Color Definitions**
            border_color = (102, 51, 0)  # Darker brown border
            roof_color_left = (160, 82, 45)  # Lighter brown for left half
            roof_color_right = (139, 69, 19)  # Darker brown for right half
            beam_color = (100, 50, 30)  # Dark brown beam in the center

            border_thickness = 4  # Thickness of the outline

            # 🏠 **Draw the border (slightly larger than the building)**
            pygame.draw.rect(screen, border_color,
                             (draw_x - border_thickness, draw_y - border_thickness,
                              self.width + border_thickness * 2, self.height + border_thickness * 2))

            # 🏠 **Draw the full rectangular roof inside the border**
            pygame.draw.rect(screen, roof_color_left, (draw_x, draw_y, self.width // 2, self.height))
            pygame.draw.rect(screen, roof_color_right, (draw_x + self.width // 2, draw_y, self.width // 2, self.height))

            # 🪵 **Draw the central beam**
            pygame.draw.rect(screen, beam_color,
                             (draw_x + self.width // 2 - 3, draw_y, 6, self.height))  # Thin vertical beam

        elif self.shape == "circle":
            pygame.draw.circle(screen, (139, 69, 19),
                               (draw_x + self.width // 2, draw_y + self.width // 2),
                               self.radius)

    def collides(self, obj_rect):
        """Checks collision based on shape type."""
        if obj_rect is None:
            return False  # Avoid errors when checking dead enemies

        if self.shape in ["square", "rectangle"]:
            inflated_rect = self.rect.inflate(-1, -1)  # Keep a slight buffer
            return inflated_rect.colliderect(obj_rect)

        elif self.shape == "circle":
            circle_x = self.rect.x + self.radius
            circle_y = self.rect.y + self.radius
            closest_x = max(obj_rect.left, min(circle_x, obj_rect.right))
            closest_y = max(obj_rect.top, min(circle_y, obj_rect.bottom))

            distance = math.sqrt((circle_x - closest_x) ** 2 + (circle_y - closest_y) ** 2)
            return distance <= self.radius


        elif self.shape == "circle":
            # Get actual center of the circle
            circle_x = self.rect.x + self.radius
            circle_y = self.rect.y + self.radius

            # Get closest point on object's bounding box to circle center
            closest_x = max(obj_rect.left, min(circle_x, obj_rect.right))
            closest_y = max(obj_rect.top, min(circle_y, obj_rect.bottom))

            distance = math.sqrt((circle_x - closest_x) ** 2 + (circle_y - closest_y) ** 2)
            return distance <= (self.radius + 1)  # Small buffer to ensure touching counts


def generate_town_layout(player_start_x=1200, player_start_y=900):
    """Generates a town-like layout with buildings and clear roads for movement."""
    obstacles = []

    # Define buildings (placed with wide roads)
    town_buildings = [
        # (x, y, width, height) - Spaced out for better movement
        (300, 200, 250, 250),  # House 1
        (800, 200, 300, 250),  # House 2
        (1400, 200, 300, 250),  # House 3
        (2000, 200, 250, 250),  # House 4

        (500, 600, 350, 300),  # Warehouse
        (1400, 600, 350, 300),  # Store

        (300, 1200, 300, 300),  # Tavern
        (1000, 1200, 400, 300),  # Market Area
        (1800, 1200, 350, 300),  # Town Hall
    ]

    # Convert building data into obstacle objects, ensuring they don’t overlap the player
    for (x, y, width, height) in town_buildings:
        obstacle_rect = pygame.Rect(x, y, width, height)

        # Ensure the obstacle doesn't spawn on the player
        player_safe_zone = pygame.Rect(player_start_x - 100, player_start_y - 100, 200, 200)
        if obstacle_rect.colliderect(player_safe_zone):
            continue  # Skip obstacles that would spawn on the player

        obstacles.append(Obstacle("rectangle", x, y, width, height))

    return obstacles