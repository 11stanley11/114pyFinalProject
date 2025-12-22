"""
The player-controlled snake.
Merged Strategy Pattern: Free Roam (Classic) & Standard (FPS).
With DEBUG features enabled.
FIXED: StandardStrategy now uses BRUTE FORCE assignment for Model Up when horizontal.
UPDATE: Vertical movement now explicitly pitches head +/- 90 degrees based on last horizontal facing (Yaw).
FIXED: A/D turning logic is now conditional based on vertical direction (Up=Inverted, Down=Normal) to match visual intuition.
"""

from ursina import *
import time
import config
from config import *

# ==========================================
# 0. Debug Helpers
# ==========================================
def create_debug_axes(parent, scale=2):
    """建立跟隨物件移動的局部座標軸 (Local Axes)"""
    # X Axis (Red) - Right
    Entity(parent=parent, model='cube', color=color.red, 
           scale=(scale, 0.05, 0.05), position=(scale/2, 0, 0))
    # Y Axis (Green) - Up
    Entity(parent=parent, model='cube', color=color.green, 
           scale=(0.05, scale, 0.05), position=(0, scale/2, 0))
    # Z Axis (Blue) - Forward
    Entity(parent=parent, model='cube', color=color.blue, 
           scale=(0.05, 0.05, scale), position=(0, 0, scale/2))

def create_world_axes(length=10, thickness=0.1):
    """建立固定在世界中心的世界座標軸 (World Axes)"""
    # World Center Marker
    Entity(model='sphere', scale=0.5, color=color.white, position=(0,0,0))
    
    # World X Axis (Red)
    Entity(model='cube', scale=(length, thickness, thickness), color=color.red, 
           position=(length/2, 0, 0), texture='white_cube')
    # World Y Axis (Green)
    Entity(model='cube', scale=(thickness, length, thickness), color=color.green, 
           position=(0, length/2, 0), texture='white_cube')
    # World Z Axis (Blue)
    Entity(model='cube', scale=(thickness, thickness, length), color=color.blue, 
           position=(0, 0, length/2), texture='white_cube')

# ==========================================
# 1. Strategies
# ==========================================

class MoveStrategy:
    def __init__(self, snake):
        self.snake = snake

    def handle_turn(self, key):
        """處理按鍵轉向輸入"""
        raise NotImplementedError
    
    def update_model_orientation(self, model):
        """
        負責更新蛇頭模型的朝向 (Rotation)。
        """
        if not model: return
        try:
            quat = Quat.from_forward_and_up(
                self.snake.direction.normalized(), 
                self.snake.up.normalized()
            )
            model.rotation = quat.euler
        except Exception:
            target_pos = self.snake.head.position + self.snake.direction.normalized()
            model.look_at(target_pos)

class FreeRoamStrategy(MoveStrategy):
    """
    自由漫遊策略 (Free Roam / Airplane Mode)
    """
    def handle_turn(self, key):
        snake = self.snake
        direction = snake.direction
        up = snake.up
        
        # Ursina Coordinate System: Up cross Forward = Right
        right = up.cross(direction).normalized()
        
        if key == 'd': # Turn Right (Yaw)
            snake.direction = right
        elif key == 'a': # Turn Left (Yaw)
            snake.direction = -right
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
    標準策略 (Standard / FPS Mode) [Strict Floor Up]
    1. 左右轉向：相對方向 (蛇的右邊)。
    2. 軸向行為：嚴格鎖定。只要在水平面移動，Green Axis (Up) 必須平行 World Y。
    """
    def __init__(self, snake):
        super().__init__(snake)
        self.orbit_axis = Vec3(0, 1, 0) # 世界中心軸 (World Up)
        
        # 初始化參考向量
        self.horizontal_forward_ref = Vec3(0, 0, 1)

    def handle_turn(self, key):
        snake = self.snake
        current_dir = snake.direction
        current_up = snake.up
        world_up = self.orbit_axis
        world_down = -world_up
        
        # 判斷是否垂直 (平行於 Orbit Axis)
        is_vertical = abs(current_dir.dot(world_up)) > 0.99
        
        new_direction = current_dir
        new_up = current_up

        if key in ('a', 'd'):
            if not is_vertical:
                # --- 水平移動時的轉向 (在紅藍平面上) ---
                local_right = current_up.cross(current_dir).normalized()
                
                if key == 'd': new_direction = local_right  # 往蛇的右邊
                else:          new_direction = -local_right # 往蛇的左邊
                
                # 強制轉正
                new_up = world_up
                self.horizontal_forward_ref = new_direction.normalized()

            else:
                # --- 垂直移動時的轉向 (在牆上) ---
                local_right = current_up.cross(current_dir).normalized()

                # [修正] 根據垂直移動的方向決定是否反轉左右
                # 向上爬 (Y > 0) 時，需要反轉 (Invert) 才能符合直覺
                # 向下爬 (Y < 0) 時，不需要反轉 (Normal)
                if current_dir.y > 0.1: # 向上
                    if key == 'd': new_direction = -local_right
                    else:          new_direction = local_right
                else: # 向下
                    if key == 'd': new_direction = local_right
                    else:          new_direction = -local_right
                
                # [關鍵修正] 從垂直轉回水平
                if abs(new_direction.dot(world_up)) < 0.01:
                    new_up = world_up # 回到地板，強制頭頂朝天
                else:
                    new_up = current_up
                
                self.horizontal_forward_ref = new_direction.normalized()

        elif key == 'w': # Pitch Up
            if current_dir != world_up and current_dir != world_down:
                new_direction = world_up
                new_up = self.horizontal_forward_ref
        
        elif key == 's': # Pitch Down
            if current_dir != world_up and current_dir != world_down:
                new_direction = world_down
                new_up = self.horizontal_forward_ref

        # 應用更新
        if new_direction.length() > 0.01 and new_direction != -current_dir:
            snake.direction = new_direction.normalized()
            snake.up = new_up.normalized()

    def update_model_orientation(self, model):
        """
        覆寫模型朝向更新邏輯 (視覺層)。
        使用最直接的屬性賦值來鎖定方向，避免 Quat 計算誤差。
        """
        if not model: return
        
        current_dir = self.snake.direction.normalized()
        world_up = self.orbit_axis # Vec3(0, 1, 0)
        
        # 判斷是否在水平面上 (方向不平行於 Y 軸)
        is_horizontal = abs(current_dir.dot(world_up)) < 0.99
        
        if is_horizontal:
            # [暴力強制修正]
            # 直接設定模型的 forward 和 up 屬性
            model.look_at(model.position + current_dir, axis='forward')
            model.rotation_z = 0 # 消除任何滾轉
            
            # 如果因為 look_at 導致 up 跑掉，再次強制修正
            yaw = math.degrees(math.atan2(current_dir.x, current_dir.z))
            model.rotation = Vec3(0, yaw, 0)
            
        else:
            # 垂直移動時 (爬牆)
            # 向上時抬頭90度，向下時低頭90度
            
            ref_dir = self.horizontal_forward_ref
            yaw = math.degrees(math.atan2(ref_dir.x, ref_dir.z))
            
            if current_dir.y > 0: # 向上
                # X = -90 代表向上看 (抬頭)
                model.rotation = Vec3(-90, yaw, 0)
            else: # 向下
                # X = 90 代表向下看 (低頭)
                model.rotation = Vec3(90, yaw, 0)


# ==========================================
# 2. Snake Entity
# ==========================================

class Snake:
    def __init__(self):
        
        # 初始化平躺
        self.body = [
            Entity(model=SNAKE_BODY_MODEL, color=SNAKE_COLOR, scale=SNAKE_BODY_SCALE, position=(0, 0, 0), collider=None),
            Entity(model=SNAKE_BODY_MODEL, color=SNAKE_COLOR, scale=SNAKE_BODY_SCALE, position=(0, 0, -1), collider=None),
            Entity(model=SNAKE_BODY_MODEL, color=SNAKE_COLOR, scale=SNAKE_BODY_SCALE, position=(0, 0, -2), collider=None)
        ]
        self.head = self.body[0]
        
        self.head_model = Entity(
            position=self.head.position
        )
        
        # Visual Mesh
        self.head_mesh = Entity(
            parent=self.head_model,
            model=SNAKE_HEAD_MODEL,                    
            scale=SNAKE_HEAD_SCALE,
            rotation_z=180, 
            rotation_y=270,
            rotation_x=180   
        )
        
        self.direction = Vec3(0, 0, 1) # Forward: Z
        self.up = Vec3(0, 1, 0)        # Up: Y
        
        self.last_move_time = time.time()
        self.turn_buffer = []
        
        self.strategies = {
            'free_roam': FreeRoamStrategy(self), 
            'standard': StandardStrategy(self)   
        }
        self.current_strategy = self.strategies['free_roam']


        self._apply_model_orientation_and_offset()
        self.update_appearance()
    
    # --- DEBUG FUNCTION ---
    def print_debug_state(self, tag="INFO"):
        def fmt(v): return f"({v.x:.2f}, {v.y:.2f}, {v.z:.2f})"
        print(f"\n--- [{tag}] ---")
        print(f"1. Logic Dir    : {fmt(self.direction)}")
        print(f"2. Logic Up     : {fmt(self.up)}")
        if self.head_model:
            print(f"3. Model Rot    : {fmt(self.head_model.rotation)}")
        print("----------------")

    def _apply_model_orientation_and_offset(self):
        if not self.head_model: return
        self.head_model.position = self.head.position
        self.current_strategy.update_model_orientation(self.head_model)
        self.head_model.position += self.direction.normalized() * 0.2

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
            
            if self.direction.length() > 0.1 and self.up.length() > 0.1:
                right = self.direction.cross(self.up).normalized()
                self.up = right.cross(self.direction).normalized()

    def update_appearance(self):
        num_segments = len(self.body)
        if self.head: self.head.enabled = False 
        if self.head_model: self.head_model.enabled = True
        
        if num_segments <= 1:
            self.head.color = SNAKE_COLOR
            return

        num_visual_segments = num_segments - 1 
        for i in range(num_visual_segments):
            segment = self.body[i + 1] 
            segment.enabled = True 
            ratio = i / (num_visual_segments - 1) if num_visual_segments > 1 else 0
            segment.color = lerp(SNAKE_HEAD_COLOR, SNAKE_COLOR, ratio)
            alpha = 1.0 - (ratio * 0.8)
            segment.color.w = alpha 

    def will_collide(self, grid_size):
        next_head_position = self.head.position + self.direction.normalized()
        half_grid = grid_size // 2
        if (next_head_position.x > half_grid or next_head_position.x < -half_grid or 
            next_head_position.y > half_grid or next_head_position.y < -half_grid or 
            next_head_position.z > half_grid or next_head_position.z < -half_grid):
            return True
        for segment in self.body[1:]:
            if next_head_position == segment.position: return True
        return False

    def move(self):
        new_head_position = self.head.position + self.direction.normalized()
        segment_to_move = self.body.pop()
        segment_to_move.position = new_head_position
        self.body.insert(0, segment_to_move)
        self.head = self.body[0]
        self._apply_model_orientation_and_offset()
        self.update_appearance()

    def grow(self):
        new_segment = Entity(model=SNAKE_BODY_MODEL, color=SNAKE_COLOR, scale=SNAKE_BODY_SCALE, position=self.body[-1].position, collider=None)
        self.body.append(new_segment)
        self.update_appearance()

    def reverse_and_grow(self):
        new_dir = Vec3(0,0,0)
        if len(self.body) < 2: new_dir = -self.direction
        else:
            new_dir = self.body[-1].position - self.body[-2].position
            if new_dir.length() < 0.1: new_dir = -self.direction

        self.body.reverse()
        self.head = self.body[0]
        
        if new_dir.length() > 0.1: self.direction = new_dir.normalized()
        else: self.direction = Vec3(0,1,0)

        if abs(self.direction.dot(self.up)) > 0.9:
            ref = Vec3(1,0,0)
            if abs(self.direction.dot(ref)) > 0.9: ref = Vec3(0,1,0)
            self.up = self.direction.cross(ref).normalized()

        self.grow()
        self.turn_buffer = []
        self.update_appearance()

    def destroy_entities(self):
        if self.head_model:
            self.head_model.disable()
            destroy(self.head_model)
            self.head_model = None
