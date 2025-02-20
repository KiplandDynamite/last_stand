import pygame

ABILITY_LIST = [
    {"name": "Speed Boost", "description": "Move 10% faster permanently.",
     "effect": lambda player: setattr(player, "move_speed_bonus", player.move_speed_bonus + 0.1) or
                              setattr(player, "speed", player.base_speed * (1 + player.move_speed_bonus))},

    {"name": "Extra Bullet", "description": "Fire one additional bullet per shot",
     "effect": lambda player: setattr(player, "bonus_bullets", player.bonus_bullets + 1)},  # ✅ Stacks bullets

    {"name": "Piercing Bullets", "description": "Bullets pass through one extra enemy",
     "effect": lambda player: setattr(player, "pierce", player.pierce + 1)},  # ✅ Stacks pierces

    {"name": "Max HP +1", "description": "Gain 1 extra HP",
     "effect": lambda player: setattr(player, "health", player.health + 1)},

    {"name": "Rapid Fire", "description": "Increase bullet fire rate by 10% per stack",
    "effect": lambda player: setattr(player, "fire_rate_multiplier", player.fire_rate_multiplier * 1.1)},

    {"name": "Adrenaline Rush", "description": "Gain 20% movement speed for 5 seconds after a kill.",
     "effect": lambda player: setattr(player, "adrenaline_boost", player.adrenaline_boost + 0.2)},

    {"name": "Ricochet Shot", "description": "Bullets bounce off walls once per level.",
    "effect": lambda player: setattr(player, "ricochet_count", player.ricochet_count + 1)},

]
