import pygame
import math
import random
from enemy import Enemy, FastEnemy, TankEnemy, DasherEnemy, ShooterEnemy, DeathAnimation, SwarmEnemy
from currency import CurrencyPickup

class SwordAttack:
    """Handles the sword attack logic."""

    def __init__(self, player):
        self.player = player
        self.cooldown = 1000  # 1-second cooldown
        self.windup_time = 200  # 200ms wind-up delay
        self.last_attack_time = 0
        self.attacking = False
        self.attack_start_time = 0
        self.attack_duration = 300  # Sword remains visible for this duration
        self.sword_angle = 0
        self.sword_offset = 80  # Distance of hilt from player center
        self.sword_length = 60  # Adjusted for bigger sword
        self.sword_width = 8  # Adjusted for bigger sword

    def can_attack(self):
        """Check if the sword attack is off cooldown."""
        return pygame.time.get_ticks() - self.last_attack_time >= self.cooldown

    def start_attack(self):
        """Begin the sword attack."""
        if self.can_attack():
            self.attacking = True
            self.attack_start_time = pygame.time.get_ticks()
            self.last_attack_time = pygame.time.get_ticks()

    def update(self, enemies, game):
        """Update sword position and check if the attack duration has ended."""
        if self.attacking:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.sword_angle = math.degrees(math.atan2(
                (mouse_y + game.camera_y) - self.player.rect.centery,
                (mouse_x + game.camera_x) - self.player.rect.centerx
            ))

            if pygame.time.get_ticks() - self.attack_start_time >= self.attack_duration:
                self.attacking = False

        # Check for enemy hits
        if self.attacking:
            self.execute_attack(enemies, game, self.player)

    def execute_attack(self, enemies, game, player):
        """Deal damage to enemies within the sword hitbox and handle XP, score, and drops."""
        """Deal damage to enemies within the sword hitbox."""
        hilt_x = self.player.rect.centerx + self.sword_offset * math.cos(math.radians(self.sword_angle))
        hilt_y = self.player.rect.centery + self.sword_offset * math.sin(math.radians(self.sword_angle))
        sword_tip_x = hilt_x + self.sword_length * math.cos(math.radians(self.sword_angle))
        sword_tip_y = hilt_y + self.sword_length * math.sin(math.radians(self.sword_angle))

        for enemy in enemies:
            if math.hypot(enemy.rect.centerx - (hilt_x + sword_tip_x) / 2,
                          enemy.rect.centery - (hilt_y + sword_tip_y) / 2) < self.sword_length / 2:
                enemy_died = enemy.take_damage()
                if enemy_died:
                    game.death_animations.append(DeathAnimation(enemy.rect.x, enemy.rect.y, enemy.rect.width))
                    enemies.remove(enemy)

                    # Score scaling for different enemies
                    if isinstance(enemy, FastEnemy):
                        game.score += 75
                        player.gain_xp(2, game)
                        drop_chance = 0.3
                        currency_amount = random.randint(1, 3)
                    elif isinstance(enemy, TankEnemy):
                        game.score += 200
                        player.gain_xp(4, game)
                        drop_chance = 0.7
                        currency_amount = random.randint(3, 7)
                    elif isinstance(enemy, DasherEnemy):
                        game.score += 100
                        player.gain_xp(6, game)
                        drop_chance = 0.5
                        currency_amount = random.randint(2, 5)
                    elif isinstance(enemy, ShooterEnemy):
                        game.score += 100
                        player.gain_xp(7, game)
                        drop_chance = 0.5
                        currency_amount = random.randint(2, 4)
                    elif isinstance(enemy, SwarmEnemy):
                        game.score += 5
                        player.gain_xp(1, game)
                        drop_chance = 0.2
                        currency_amount = 1
                    else:
                        game.score += 50
                        player.gain_xp(1, game)
                        drop_chance = 0.4
                        currency_amount = random.randint(1, 2)

                    # Drop Currency on the Gameboard (Random Chance)
                    if random.random() < drop_chance:
                        currency_pickup = CurrencyPickup(enemy.rect.centerx, enemy.rect.centery, currency_amount)
                        game.currency_drops.append(currency_pickup)

    def draw(self, screen, game):
        """Draw a simple sword-like shape following the cursor direction, ensuring the hilt rotates around the player."""
        if self.attacking:
            # Calculate sword hilt position along a circular path around the player
            hilt_x = self.player.rect.centerx + self.sword_offset * math.cos(math.radians(self.sword_angle))
            hilt_y = self.player.rect.centery + self.sword_offset * math.sin(math.radians(self.sword_angle))

            # Calculate sword tip and base
            tip_x = hilt_x + self.sword_length * math.cos(math.radians(self.sword_angle))
            tip_y = hilt_y + self.sword_length * math.sin(math.radians(self.sword_angle))
            base_x = hilt_x - (self.sword_length * 0.3) * math.cos(math.radians(self.sword_angle))
            base_y = hilt_y - (self.sword_length * 0.3) * math.sin(math.radians(self.sword_angle))

            # Calculate side points for width
            left_x = base_x + self.sword_width * math.cos(math.radians(self.sword_angle + 90))
            left_y = base_y + self.sword_width * math.sin(math.radians(self.sword_angle + 90))
            right_x = base_x + self.sword_width * math.cos(math.radians(self.sword_angle - 90))
            right_y = base_y + self.sword_width * math.sin(math.radians(self.sword_angle - 90))

            # Draw sword shape
            pygame.draw.polygon(screen, (200, 200, 200), [
                (tip_x - game.camera_x, tip_y - game.camera_y),
                (left_x - game.camera_x, left_y - game.camera_y),
                (right_x - game.camera_x, right_y - game.camera_y)
            ])
