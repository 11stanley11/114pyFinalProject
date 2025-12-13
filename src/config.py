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
SNAKE_BODY_MODLE = '../assets/snkb.obj'
SNAKE_HEAD_MODLE = '../assets/snhd.obj'

#Scale
SNAKE_BODY_SCALE = 0.5
SNAKE_HEAD_SCALE = 0.75
# Colors
BACKGROUND_COLOR = color.rgba32(205,216,233,a=255)
SNAKE_COLOR = color.rgba32(33,78,175,a=255)
SNAKE_HEAD_COLOR = color.rgba32(77,123,243,a=255)
FOOD_COLOR = color.rgba32(232,72,31,a=255)
OBSTACLE_COLOR = color.gray
GRID_COLOR = color.gray
BOUNDARY_COLOR = color.rgba32(86,139,52,a=255)

AI_COLOR = color.orange
AI_SPEED = 2  # Make it slightly slower than player so it's fair
