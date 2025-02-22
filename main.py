import pygame

# Initialize Pygame
pygame.init()

import sys
from game import Game
from leaderboard import load_leaderboard, save_leaderboard

# Constants
WIDTH, HEIGHT = 1024, 768
WHITE = (255, 255, 255)
FONT = pygame.font.Font(None, 36)

# Menu background texture
MENU_BACKGROUND = pygame.image.load("textures/Menu.webp")  # Update path if needed
MENU_BACKGROUND = pygame.transform.scale(MENU_BACKGROUND, (WIDTH, HEIGHT))  # Resize to fit screen
# Leaderboard background texture
LEADERBOARD_BACKGROUND = pygame.image.load("textures/leaderboard_background.webp")  # Update path if needed
LEADERBOARD_BACKGROUND = pygame.transform.scale(LEADERBOARD_BACKGROUND, (WIDTH, HEIGHT))  # Resize to fit screen


# Set up screen (GLOBAL)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Last Stand")

def main_menu():
    while True:
        # 🖼️ **Apply the menu background**
        screen.blit(MENU_BACKGROUND, (0, 0))

        # 🖲️ **Draw buttons with rounded corners & outline**
        draw_button("Start Game", WIDTH // 2 - 100, 300, 200, 50, lambda: Game().run())
        draw_button("Leaderboard", WIDTH // 2 - 100, 400, 200, 50, show_leaderboard)

        pygame.display.flip()

        # Handle quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def show_leaderboard():
    """Displays the leaderboard and properly formats 'waves' instead of 'seconds'."""
    scores = load_leaderboard()
    while True:
        # 🖼️ **Apply the leaderboard background**
        screen.blit(LEADERBOARD_BACKGROUND, (0, 0))

        y_offset = 150
        backdrop_color = (20, 20, 20, 180)  # Semi-transparent dark gray
        backdrop_height = 35  # Standardized height

        # 📏 **Find the longest text width**
        longest_text_width = max(FONT.render(f"{entry[0]} - Waves: {entry[1]}, Score: {entry[2]}", True, WHITE).get_width() for entry in scores)
        backdrop_width = longest_text_width + 40  # Add padding to ensure spacing

        for entry in scores:
            text = f"{entry[0]} - Waves: {entry[1]}, Score: {entry[2]}"

            # 🎨 **Create outlined text**
            outline_color = (50, 50, 50)  # Dark outline
            text_surface = FONT.render(text, True, WHITE)
            outline = FONT.render(text, True, outline_color)

            # 📦 **Draw backdrop rectangle based on longest text width**
            backdrop_rect = pygame.Surface((backdrop_width, backdrop_height), pygame.SRCALPHA)
            backdrop_rect.fill(backdrop_color)
            screen.blit(backdrop_rect, (WIDTH // 2 - backdrop_width // 2, y_offset - 5))

            # **Draw outline by offsetting in four directions**
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                screen.blit(outline, (WIDTH // 2 - outline.get_width() // 2 + dx, y_offset + dy))

            # **Draw main text on top**
            screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, y_offset))

            y_offset += 40  # Keep spacing consistent

        # 🏠 **Back to Main Menu Button**
        draw_button("Back to Menu", WIDTH // 2 - 100, HEIGHT - 120, 200, 50, main_menu)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()




def draw_button(text, x, y, width, height, action=None):
    """Draws a rounded button with an outline, hover effect, and click handling."""
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # 🎨 Button colors
    button_color = (50, 50, 50)  # Default dark gray
    hover_color = (100, 100, 100)  # Lighter gray when hovered
    outline_color = (200, 200, 200)  # Light gray outline
    text_color = WHITE
    border_radius = 15  # Curve the button edges

    # Check if mouse is over button
    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, hover_color, (x, y, width, height), border_radius=border_radius)
        if click[0] == 1 and action:  # Left mouse click
            pygame.time.delay(150)  # Prevent multiple clicks
            action()
    else:
        pygame.draw.rect(screen, button_color, (x, y, width, height), border_radius=border_radius)

    # 🖼️ **Draw button outline**
    pygame.draw.rect(screen, outline_color, (x, y, width, height), 3, border_radius=border_radius)

    # 📝 Render text centered on the button
    text_surface = FONT.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)


if __name__ == "__main__":
    main_menu()
