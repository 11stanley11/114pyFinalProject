"""
Game configuration settings.
"""

from ursina import color

# Screen settings
FULLSCREEN = False

# Game settings
GRID_SIZE = 8
MAX_GRID_SIZE = 12
SNAKE_SPEED = 3

# Colors
BACKGROUND_COLOR = color.dark_gray
SNAKE_COLOR = color.green
FOOD_COLOR = color.red
OBSTACLE_COLOR = color.gray
GRID_COLOR = color.gray
BOUNDARY_COLOR = color.light_gray

AI_COLOR = color.orange
AI_SPEED = 2  # Make it slightly slower than player so it's fair