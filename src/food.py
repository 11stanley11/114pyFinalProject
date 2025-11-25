"""
Food for the snake.
"""

from ursina import Entity
import random
from config import FOOD_COLOR, GRID_SIZE

class Food(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=FOOD_COLOR,
            scale=1,
            position=self.random_position()
        )

    def random_position(self):
        half_grid = GRID_SIZE // 2
        return (
            random.randint(-half_grid + 1, half_grid - 1),
            random.randint(-half_grid + 1, half_grid - 1),
            random.randint(-half_grid + 1, half_grid - 1)
        )

    def reposition(self):
        self.position = self.random_position()
