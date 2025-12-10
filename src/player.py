"""
The player-controlled snake.
Merged Strategy Pattern: Free Roam (Classic) & Standard (FPS).
"""

from ursina import Entity, Vec3, color, Vec4
import time
from config import SNAKE_SPEED, SNAKE_COLOR, GRID_SIZE

# Use the border color logic if desired, or keep simple
BORDER_COLOR = color.rgb(20, 20, 20) 

# ==========================================
# 1. Strategies
# ==========================================

class MoveStrategy:
    def __init__(self, snake):
        self.snake = snake

    def handle_turn(self, key):
        raise NotImplementedError

class FreeRoamStrategy(MoveStrategy):
    """
    Your current (Classic) logic.
    Best for: Follow/Classic Camera.
    """
    def handle_turn(self, key):
        snake = self.snake
        direction = snake.direction
        up = snake.up
        
        right = direction.cross(up).normalized()
        
        if key == 'd': # Turn Right
            snake.direction = -right
        elif key == 'a': # Turn Left
            snake.direction = right
        elif key == 'w': # Pitch Up
            new_direction = up
            snake.up = -direction
            snake.direction = new_direction
        elif key == 's': # Pitch Down
            new_direction = -up
            snake.up = direction
            snake.direction = new_direction
        elif key == 'e': # Roll Left
            snake.up = -right
        elif key == 'q': # Roll Right
            snake.up = right

class StandardStrategy(MoveStrategy):
    """
    From Collaborator (FPS / Gravity Locked).
    Best for: Orbital & TopDown Camera.
    """
    def __init__(self, snake):
        super().__init__(snake)
        self.horizontal_right_ref = Vec3(1, 0, 0)
        self.horizontal_forward_ref = Vec3(0, 0, 1)

    def handle_turn(self, key):
        snake = self.snake
        current_dir = snake.direction
        
        # Calculate Right vector
        right = current_dir.cross(snake.up)
        if right.length() < 0.01: right = Vec3(1,0,0)
        right = right.normalized()
        
        new_direction = current_dir
        new_up = snake.up
        
        world_up = Vec3(0, 1, 0)
        world_down = Vec3(0, -1, 0)
        is_vertical = abs(current_dir.y) > 0.99

        if key in ('a', 'd'):
            if not is_vertical:
                # Standard Yaw
                if key == 'd': new_direction = -right
                else:          new_direction = right

                # If moving flat, align up with world up
                if abs(new_direction.y) < 0.01:
                    new_up = world_up
                    self.horizontal_right_ref = right
                    self.horizontal_forward_ref = new_direction.normalized()
            else:
                # Vertical Yaw (spin on axis)
                ref_right = self.horizontal_forward_ref.cross(world_up).normalized()
                if key == 'd': new_direction = -ref_right.normalized()
                else:          new_direction = ref_right.normalized()
                new_up = world_up

        elif key == 'w': # Pitch Up
            if current_dir != world_up and current_dir != world_down:
                new_direction = world_up
                new_up = self.horizontal_forward_ref
        
        elif key == 's': # Pitch Down
            if current_dir != world_up and current_dir != world_down:
                new_direction = world_down
                new_up = self.horizontal_forward_ref

        # Apply changes if valid
        if new_direction.length() > 0.01 and new_direction != -current_dir:
            snake.direction = new_direction.normalized()
            snake.up = new_up.normalized()


# ==========================================
# 2. Snake Entity
# ==========================================

class Snake:
    def __init__(self):
        # Keep original appearance logic (simple cubes)
        self.body = [
            Entity(model='cube', color=SNAKE_COLOR, scale=1, position=(0, 0, 0)),
            Entity(model='cube', color=SNAKE_COLOR, scale=1, position=(0, -1, 0)),
            Entity(model='cube', color=SNAKE_COLOR, scale=1, position=(0, -2, 0))
        ]
        self.head = self.body[0]
        
        self.direction = Vec3(0, 1, 0) 
        self.up = Vec3(0, 0, 1) 
        
        self.last_move_time = time.time()
        self.turn_buffer = []

        # Strategy Manager
        self.strategies = {
            'free_roam': FreeRoamStrategy(self), 
            'standard': StandardStrategy(self)   
        }
        self.current_strategy = self.strategies['free_roam'] # Default

        self.update_appearance()

    def set_strategy(self, name):
        if name in self.strategies:
            self.current_strategy = self.strategies[name]

    def turn(self, key):
        if len(self.turn_buffer) < 3:
            self.turn_buffer.append(key)

    def handle_turn(self):
        if self.turn_buffer:
            key = self.turn_buffer.pop(0)
            self.current_strategy.handle_turn(key)

    def update_appearance(self):
        # Original Appearance Logic
        num_segments = len(self.body)
        if num_segments <= 1:
            self.head.color = SNAKE_COLOR
            return

        for i, segment in enumerate(self.body):
            alpha = 1.0 - (i / (num_segments - 1)) * 0.8
            segment.color = color.Color(SNAKE_COLOR.r, SNAKE_COLOR.g, SNAKE_COLOR.b, alpha)

    def will_collide(self, grid_size):
        next_head_position = self.head.position + self.direction.normalized()
        half_grid = grid_size // 2

        if (next_head_position.x > half_grid or next_head_position.x < -half_grid or 
            next_head_position.y > half_grid or next_head_position.y < -half_grid or 
            next_head_position.z > half_grid or next_head_position.z < -half_grid):
            return True

        for segment in self.body[1:]:
            if next_head_position == segment.position:
                return True
        return False

    def move(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].position = self.body[i - 1].position

        self.head.position += self.direction.normalized()

    def grow(self):
        new_segment = Entity(model='cube', color=SNAKE_COLOR, scale=1, position=self.body[-1].position)
        self.body.append(new_segment)
        self.update_appearance()