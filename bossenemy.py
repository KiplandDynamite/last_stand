import pygame
import random
import math
from enemy import Enemy, EliteShooter
from missile import Missile  # Assuming we create a Missile class separately


class BossEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=150)
        self.rect = pygame.Rect(x, y, 100, 100)  # Override size
        self.base_speed = 0.75  # Normal movement speed
        self.dash_speed = 100  # Much faster dash speed for dashing
        self.speed = self.base_speed
        self.summon_timer = 0  # Timer for summoning Elite Shooters
        self.missile_timer = 0  # Timer for launching homing missiles
        self.dash_cooldown = 3000  # 3-second cooldown between dashes
        self.charge_time = 800  # 0.8-second warning before dashing
        self.last_dash_time = pygame.time.get_ticks()
        self.is_charging = False
        self.charge_start_time = 0
        self.missile_cooldown = 3000  # Fire missile every 3 seconds
        self.summon_cooldown = 25000  # Summon Elite Shooters every 25 seconds
        self.last_missile_time = pygame.time.get_ticks()
        self.target = None  # Player target reference (set externally)
        self.color = (0, 0, 0)  # Set Boss color to black
        self.hit_timer = 0
        self.hit_effect_duration = 150  # Duration of hit flash effect
        self.is_dying = False

    def update(self, player, obstacles, game, enemy_bullets=None):
        """ Updates Boss logic, including movement, attacks, and summons. """
        super().update(player, obstacles, game)  # Keeps base movement logic

        current_time = pygame.time.get_ticks()
        distance_to_player = math.sqrt(
            (player.rect.centerx - self.rect.centerx) ** 2 + (player.rect.centery - self.rect.centery) ** 2)

        # Ensure boss has a target
        if self.target is None:
            self.target = player

        # Start charging phase if close enough and cooldown is up
        if distance_to_player < 200 and current_time - self.last_dash_time > self.dash_cooldown and not self.is_charging:
            self.is_charging = True
            self.charge_start_time = current_time  # Store charge start time
            self.speed = 0  # Stop moving during charge phase

        # After charge_time, actually dash
        if self.is_charging and current_time - self.charge_start_time > self.charge_time:
            self.is_charging = False
            self.speed = self.dash_speed
            self.last_dash_time = current_time  # Reset cooldown

        # If not charging, return to normal movement speed
        elif not self.is_charging:
            self.speed = self.base_speed

        # Missile attack logic
        if current_time - self.last_missile_time >= self.missile_cooldown:
            self.fire_missile(game)
            self.last_missile_time = current_time

        # Summon Elite Shooters
        self.summon_timer += 1
        if self.summon_timer >= self.summon_cooldown:
            self.summon_elite_shooters(game)
            self.summon_timer = 0

    def fire_missile(self, game):
        """ Fires a homing missile at the player. """
        if self.target:
            missile = Missile(self.rect.centerx, self.rect.centery, self.target)
            game.enemies.append(missile)

    def summon_elite_shooters(self, game):
        """ Summons 3 Elite Shooters randomly around the arena. """
        for _ in range(3):
            spawn_x = random.randint(100, 2400)  # Adjust based on map size
            spawn_y = random.randint(100, 1800)
            elite = EliteShooter(spawn_x, spawn_y)
            game.enemies.append(elite)

    def take_damage(self, amount):
        """Handles damage taken by the Boss. Does not remove Boss instantly."""
        self.health -= amount
        self.hit_timer = pygame.time.get_ticks()  # Trigger hit effect

        if self.health <= 0 and not self.is_dying:
            self.is_dying = True
            self.death_timer = pygame.time.get_ticks()

    def draw(self, screen, camera_x, camera_y):
        """Draws the boss with a black outline, hit effect, and health bar."""
        if self.rect is None:
            return  # Don't draw if the boss is removed

        current_time = pygame.time.get_ticks()
        outline_color = (0, 0, 0)  # Default black outline
        base_color = (50, 50, 50)  # Dark gray for boss

        # Damage effect
        if current_time - self.hit_timer < self.hit_effect_duration:
            boss_color = (255, 255, 255)  # White flash
            outline_color = (255, 0, 0)  # Red outline on hit
        elif self.is_dying:
            boss_color = (255, 255, 255)  # White flash on death
        else:
            boss_color = base_color

        # Shrink slightly when dying
        shrink_factor = 0.75 if self.is_dying else 1.0
        width, height = int(self.rect.width * shrink_factor), int(self.rect.height * shrink_factor)
        draw_x = self.rect.x - camera_x + (self.rect.width - width) // 2
        draw_y = self.rect.y - camera_y + (self.rect.height - height) // 2

        # Draw outline
        pygame.draw.rect(screen, outline_color,
                         pygame.Rect(draw_x - 3, draw_y - 3, width + 6, height + 6))

        # Draw boss
        pygame.draw.rect(screen, boss_color, pygame.Rect(draw_x, draw_y, width, height))

        # Draw health bar
        if not self.is_dying:
            self.draw_health_bar(screen, camera_x, camera_y, boss_color)

    def draw_health_bar(self, screen, camera_x, camera_y, color):
        """ Draws the boss's health bar above its head. """
        bar_width = self.rect.width
        bar_height = 5
        health_percentage = max(self.health / 150, 0)  # Normalize health
        health_bar_rect = pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y - 10,
                                      bar_width * health_percentage, bar_height)
        pygame.draw.rect(screen, (0, 255, 0), health_bar_rect)  # Green health bar
