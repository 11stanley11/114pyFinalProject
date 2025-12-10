"""
Food for the snake.
"""

from ursina import Entity
import random
from config import FOOD_COLOR, GRID_SIZE

class Food(Entity):
    def __init__(self, occupied_positions=None):
        if occupied_positions is None: occupied_positions = []
        super().__init__(
            model='cube',
            color=FOOD_COLOR,
            scale=1,
            position=self.get_valid_position(occupied_positions)
        )

    def random_position(self):
        half_grid = GRID_SIZE // 2
        return (
            random.randint(-half_grid + 1, half_grid - 1),
            random.randint(-half_grid + 1, half_grid - 1),
            random.randint(-half_grid + 1, half_grid - 1)
        )

    def get_valid_position(self, occupied_positions):
        # Try to find a valid position up to 100 times to prevent infinite loops
        for _ in range(100):
            pos = self.random_position()
            # Convert pos tuple to Vec3 logic if needed, or just compare values
            # Ursina positions are Vec3, occupied_positions likely contains Vec3 or tuples
            is_occupied = False
            for occ in occupied_positions:
                # Compare rounded positions to handle float inaccuracies
                if round(occ.x) == pos[0] and round(occ.y) == pos[1] and round(occ.z) == pos[2]:
                    is_occupied = True
                    break
            
            if not is_occupied:
                return pos
        
        # Fallback if grid is super full
        return self.random_position()

    def reposition(self, occupied_positions=[]):
        self.position = self.get_valid_position(occupied_positions)
