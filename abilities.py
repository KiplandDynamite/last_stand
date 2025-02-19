ABILITY_LIST = [
    {"name": "Speed Boost", "description": "Move 20% faster",
     "effect": lambda player: setattr(player, "speed", player.speed * 1.2)},

    {"name": "Extra Bullet", "description": "Fire one additional bullet per shot",
     "effect": lambda player: setattr(player, "bonus_bullets", player.bonus_bullets + 1)},  # ✅ Stacks bullets

    {"name": "Piercing Bullets", "description": "Bullets pass through one extra enemy",
     "effect": lambda player: setattr(player, "pierce", player.pierce + 1)},  # ✅ Stacks pierces

    {"name": "Max HP +1", "description": "Gain 1 extra HP",
     "effect": lambda player: setattr(player, "health", player.health + 1)},
]
