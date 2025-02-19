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

# Set up screen (GLOBAL)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Last Stand")

def main_menu():
    while True:
        screen.fill((30, 30, 30))
        title = FONT.render("Last Stand", True, WHITE)
        play_text = FONT.render("Press ENTER to Play", True, WHITE)
        leaderboard_text = FONT.render("Press L to View Leaderboard", True, WHITE)

        screen.blit(title, (WIDTH // 2 - 100, 100))
        screen.blit(play_text, (WIDTH // 2 - 150, 300))
        screen.blit(leaderboard_text, (WIDTH // 2 - 200, 400))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game = Game()
                    game.run()
                if event.key == pygame.K_l:
                    show_leaderboard()

def show_leaderboard():
    """Displays the leaderboard and properly formats 'waves' instead of 'seconds'."""
    scores = load_leaderboard()
    while True:
        screen.fill((30, 30, 30))
        title = FONT.render("Leaderboard", True, WHITE)

        # Center leaderboard title
        title_rect = title.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title, title_rect)

        y_offset = 200
        for entry in scores:
            text = f"{entry[0]} - Waves: {entry[1]}, Score: {entry[2]}"  # Changed "Time" to "Waves"
            score_text = FONT.render(text, True, WHITE)

            # Center each line dynamically
            text_rect = score_text.get_rect(center=(WIDTH // 2, y_offset))
            screen.blit(score_text, text_rect)

            y_offset += 40

        # Instructions for returning to main menu
        return_text = FONT.render("Press ENTER to return to Main Menu", True, WHITE)
        return_rect = return_text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        screen.blit(return_text, return_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                main_menu()


if __name__ == "__main__":
    main_menu()
