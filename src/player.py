"""
The player-controlled snake.
Merged Strategy Pattern: Free Roam (Classic) & Standard (FPS).
"""

from ursina import Entity, Vec3, color
import time

SNAKE_COLOR = color.green
# 設定邊框顏色，深灰色在黑色背景上會形成自然的間隙感
BORDER_COLOR = color.rgb(20, 20, 20) 
GRID_SIZE = 20

# ==========================================
# 1. 策略介面與具體實作
# ==========================================

class MoveStrategy:
    def __init__(self, snake):
        self.snake = snake

    def handle_turn(self, key):
        raise NotImplementedError

    def get_name(self):
        return "Unknown Mode"

class FreeRoamStrategy(MoveStrategy):
    """模式 A: 完全相對移動 (6DOF) - 安全版"""
    def get_name(self):
        return "Free Roam (6DOF)"

    def handle_turn(self, key):
        snake = self.snake
        
        current_dir = snake.direction
        current_up = snake.up

        if current_dir.length() < 0.01:
            if abs(current_up.y) > 0.9:
                current_dir = Vec3(0, 0, 1)
            else:
                current_dir = current_up.cross(Vec3(0, 1, 0))
                if current_dir.length() < 0.01:
                    current_dir = current_up.cross(Vec3(1, 0, 0))
            current_dir = current_dir.normalized()

        try:
            right = current_dir.cross(current_up)
            if right.length() < 0.01:
                right = Vec3(1,0,0)
            else:
                right = right.normalized()
        except:
            right = Vec3(1,0,0)

        new_direction = current_dir
        new_up = current_up

        if key == 'd':   # Turn Right (Yaw)
            new_direction = right
            new_up = current_up
            
        elif key == 'a': # Turn Left (Yaw)
            new_direction = -right
            new_up = current_up
        
        elif key == 'w': # Pitch Up
            new_direction = current_up
            new_up = -current_dir
            
        elif key == 's': # Pitch Down
            new_direction = -current_up
            new_up = current_dir
            
        elif key == 'e': # Roll Left
            new_up = -right
        elif key == 'q': # Roll Right
            new_up = right
        
        if new_direction.length() > 0.01 and new_up.length() > 0.01:
            snake.direction = new_direction.normalized()
            snake.up = new_up.normalized()

class StandardStrategy(MoveStrategy):
    """模式 B: 標準 3D 導航 (FPS Style) - 安全版"""
    def __init__(self, snake):
        super().__init__(snake)
        self.horizontal_right_ref = Vec3(1, 0, 0)
        self.horizontal_forward_ref = Vec3(0, 0, 1)

    def get_name(self):
        return "Standard (Gravity Locked)"

    def handle_turn(self, key):
        snake = self.snake
        
        current_dir = snake.direction
        if current_dir.length() < 0.01:
            if self.horizontal_forward_ref.length() > 0.01:
                current_dir = self.horizontal_forward_ref
            else:
                current_dir = Vec3(0, 0, 1)

        right = current_dir.cross(snake.up)
        if right.length() < 0.01: right = Vec3(1,0,0)
        right = right.normalized()
        
        new_direction = current_dir
        new_up = snake.up
        
        world_up_dir = Vec3(0, 1, 0)
        world_down_dir = Vec3(0, -1, 0)
        is_currently_vertical = abs(current_dir.y) > 0.99

        if key in ('a', 'd'):
            if not is_currently_vertical:
                if key == 'd': new_direction = -right
                else:          new_direction = right

                if abs(new_direction.y) < 0.01:
                    new_up = world_up_dir
                    self.horizontal_right_ref = right
                    self.horizontal_forward_ref = new_direction.normalized()
                else:
                    new_up = snake.up 
            else:
                ref_right = self.horizontal_forward_ref.cross(world_up_dir).normalized()
                if key == 'd': new_direction = -ref_right.normalized()
                else:          new_direction = ref_right.normalized()
                new_up = world_up_dir

        elif key == 'w': 
            if current_dir.normalized() != world_up_dir and \
               current_dir.normalized() != -world_up_dir:
                new_direction = world_up_dir
                new_up = self.horizontal_forward_ref
        
        elif key == 's': 
            if current_dir.normalized() != world_down_dir and \
               current_dir.normalized() != -world_down_dir:
                new_direction = world_down_dir
                new_up = self.horizontal_forward_ref

        if new_direction.length() > 0.01:
             if new_direction.normalized() != -current_dir.normalized():
                snake.direction = new_direction.normalized()
                snake.up = new_up.normalized()

# ==========================================
# 2. 貪吃蛇實體
# ==========================================

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
    def _create_segment(self, position):
        """
        建立一個帶有邊框的身體節點
        【重要修正】已移至 __init__ 之前，確保類別能正確識別此方法
        """
        # 父物件：作為邊框與碰撞體
        segment = Entity(model='cube', color=BORDER_COLOR, scale=1, position=position)
        
        # 子物件：作為實際的顏色顯示
        segment.inner = Entity(parent=segment, model='cube', color=SNAKE_COLOR, scale=0.85)
        
        return segment

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
        new_segment = self._create_segment(self.body[-1].position)
        self.body.append(new_segment)
        self.update_appearance()
