"""
The player-controlled snake.
"""

from ursina import Entity, Vec3, color, Vec4
import time
from config import SNAKE_SPEED, SNAKE_COLOR, GRID_SIZE

class Snake:
    def __init__(self):
        self.body = [
            Entity(model='cube', color=SNAKE_COLOR, scale=1, position=(0, 0, 0)),
            Entity(model='cube', color=SNAKE_COLOR, scale=1, position=(0, -1, 0)),
            Entity(model='cube', color=SNAKE_COLOR, scale=1, position=(0, -2, 0))
        ]
        self.head = self.body[0]
        self.head_marker = Entity(model='cube', color=color.yellow, scale=(0.5, 0.1, 0.5))
        self.direction = Vec3(0, 1, 0)  # Start moving up
        self.up = Vec3(0, 0, 1) # A vector to keep track of the snake's orientation
        self.last_move_time = time.time()
        self.turn_buffer = []
        self.update_appearance()

    def turn(self, key):
        # Limit the number of buffered turns to avoid chaotic spinning
        if len(self.turn_buffer) < 3:
            self.turn_buffer.append(key)

    def update_appearance(self):
        num_segments = len(self.body)
        if num_segments <= 1:
            self.head.color = SNAKE_COLOR
            return

        for i, segment in enumerate(self.body):
            alpha = 1.0 - (i / (num_segments - 1)) * 0.8  # alpha from 1.0 down to 0.2
            segment.color = color.Color(SNAKE_COLOR.r, SNAKE_COLOR.g, SNAKE_COLOR.b, alpha)



    def handle_turn(self):
        if self.turn_buffer:
            key = self.turn_buffer.pop(0)
            
            right = self.direction.cross(self.up).normalized()
            
            if key == 'd': # Turn Left
                self.direction = -right
            elif key == 'a': # Turn Right
                self.direction = right
            elif key == 'w': # Turn Up
                new_direction = self.up
                self.up = -self.direction
                self.direction = new_direction
            elif key == 's': # Turn Down
                new_direction = -self.up
                self.up = self.direction
                self.direction = new_direction
            # 'q' and 'e' for roll
            elif key == 'e': # Roll Left
                self.up = -right
            elif key == 'q': # Roll Left
                self.up = right

    def will_collide(self, grid_size):
        """
        Checks if the snake will collide with walls or itself on its next move.
        """
        next_head_position = self.head.position + self.direction.normalized()
        half_grid = grid_size // 2

        # Wall collision
        if (next_head_position.x > half_grid or next_head_position.x < -half_grid or 
            next_head_position.y > half_grid or next_head_position.y < -half_grid or 
            next_head_position.z > half_grid or next_head_position.z < -half_grid):
            return True

        # Self collision
        for segment in self.body[1:]:
            if next_head_position == segment.position:
                return True

        return False

    def move(self):
        # --- Move body ---
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].position = self.body[i - 1].position

        # --- Move head ---
        self.head.position += self.direction.normalized()

        # --- Update head marker ---
        self.head_marker.position = self.head.position + self.up * 0.5
        self.head_marker.world_up = self.up
        self.head_marker.look_at(self.head.position + self.direction)

    def grow(self):
        new_segment = Entity(model='cube', color=SNAKE_COLOR, scale=1, position=self.body[-1].position)
        self.body.append(new_segment)
        self.update_appearance()
