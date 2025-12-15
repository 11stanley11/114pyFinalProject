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
#Model
SNAKE_BODY_MODLE = 'snkb'
SNAKE_HEAD_MODLE = 'snhd'
SNAKE_FOOD_MODLE = 'apple'
#Scale
SNAKE_BODY_SCALE = 0.4
SNAKE_HEAD_SCALE = 0.7
FOOD_SCALE = 0.5
# Colors
BACKGROUND_COLOR = color.hex("#FFFFFF")
SNAKE_COLOR = color.hex('#1644a1')
SNAKE_HEAD_COLOR = color.hex('#4c7ae8')
FOOD_COLOR = color.hex('#EA4335')
OBSTACLE_COLOR = color.gray
GRID_COLOR = color.hex('#93C46C')
BOUNDARY_COLOR = color.hex("#5C5C5C")

AI_COLOR = color.orange
AI_SPEED = 2  # Make it slightly slower than player so it's fair
