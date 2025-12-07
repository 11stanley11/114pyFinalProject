"""
Player controlled snake entity with Strategy Pattern for movement.
Update: Moved _create_segment before __init__ to guarantee scope visibility.
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
        self.body = []
        
        # 建立初始身體 (3節)
        for i in range(3):
            pos = (0, -i, 0)
            # 現在 _create_segment 已經定義在上面，這裡一定找得到
            self.body.append(self._create_segment(pos))
            
        self.head = self.body[0]
        self.head_marker = Entity(model='cube', color=color.yellow, scale=(0.5, 0.1, 0.5))
        
        self.direction = Vec3(0, 1, 0) 
        self.up = Vec3(0, 0, 1)

        self.last_move_time = time.time()
        self.turn_buffer = []

        self.strategies = {
            '2': FreeRoamStrategy(self), 
            '1': StandardStrategy(self)  
        }
        self.current_strategy = self.strategies['1'] 
        print(f"Current Mode: {self.current_strategy.get_name()}")
        self.update_appearance()

    def turn(self, key):
        if key in self.strategies:
            self.current_strategy = self.strategies[key]
            print(f"Switched to: {self.current_strategy.get_name()}")
            self.turn_buffer = [] 
            return
        
        mapped_key = key
        if key == 'gamepad a': mapped_key = '1'
        elif key == 'gamepad b': mapped_key = '2'
        
        elif key == 'gamepad y': mapped_key = 'q'
        elif key == 'gamepad left shoulder': mapped_key = 'e'
        
        if len(self.turn_buffer) < 3:
            if mapped_key in ['w', 's', 'a', 'd', 'q', 'e']:
                self.turn_buffer.append(mapped_key)

    def handle_turn(self):
        if self.turn_buffer:
            key = self.turn_buffer.pop(0)
            self.current_strategy.handle_turn(key)

    def will_collide(self, grid_size=GRID_SIZE):
        if self.direction.length() < 0.001: return False 
        
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
        if self.direction.length() < 0.001:
            self.direction = Vec3(0,1,0)

        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].position = self.body[i - 1].position

        self.head.position += self.direction.normalized()

        self.head_marker.position = self.head.position
        self.head_marker.world_up = self.up
        self.head_marker.look_at(self.head.position + self.direction)

    def grow(self):
        new_segment = self._create_segment(self.body[-1].position)
        self.body.append(new_segment)
        self.update_appearance()

    def update_appearance(self):
        num_segments = len(self.body)
        if num_segments <= 1:
            # 頭部依然保持綠色
            self.head.inner.color = SNAKE_COLOR
            return
            
        for i, segment in enumerate(self.body):
            alpha = 1.0 - (i / (num_segments - 1)) * 0.8 
            
            # 更新內層 (身體) 的顏色與透明度
            if hasattr(segment, 'inner'):
                segment.inner.color = color.Color(SNAKE_COLOR.r, SNAKE_COLOR.g, SNAKE_COLOR.b, alpha)
            
            # 更新外層 (邊框) 的透明度
            segment.color = color.Color(BORDER_COLOR.r, BORDER_COLOR.g, BORDER_COLOR.b, alpha)