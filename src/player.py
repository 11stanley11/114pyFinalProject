"""
The player-controlled snake.
Merged Strategy Pattern: Free Roam (Classic) & Standard (FPS).
With DEBUG features enabled.
FIXED: StandardStrategy visual glitches fixed by using Quaternion rotation instead of look_at.
FIXED: StandardStrategy now correctly updates reference vectors when turning from vertical to horizontal.
"""

from ursina import *
import time
import config
from config import *

# ==========================================
# 0. Debug Helpers
# ==========================================
def create_debug_axes(parent, scale=2):
    # X Axis (Red) - Right
    Entity(parent=parent, model='cube', color=color.red, 
           scale=(scale, 0.05, 0.05), position=(scale/2, 0, 0))
    # Y Axis (Green) - Up
    Entity(parent=parent, model='cube', color=color.green, 
           scale=(0.05, scale, 0.05), position=(0, scale/2, 0))
    # Z Axis (Blue) - Forward
    Entity(parent=parent, model='cube', color=color.blue, 
           scale=(0.05, 0.05, scale), position=(0, 0, scale/2))

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
        修正：使用 Quat.from_forward_and_up 來確保所有角度 (包含垂直移動) 都正確。
        這解決了 Standard 模式下爬牆時蛇頭亂轉的問題。
        """
        if not model: return
        
        try:
            # 嘗試使用 Quaternion 計算旋轉，這是最穩定的 3D 朝向方法
            # 它會嚴格遵守 snake.direction (前方) 和 snake.up (上方)
            quat = Quat.from_forward_and_up(
                self.snake.direction.normalized(), 
                self.snake.up.normalized()
            )
            model.rotation = quat.euler
        except Exception as e:
            # 如果 Quat 計算失敗 (極少見，除非向量長度為0)，退回 look_at
            # print(f"Quat Error: {e}, falling back to look_at")
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
        
        right = direction.cross(up).normalized()
        
        if key == 'd': # Turn Right (Yaw)
            snake.direction = -right
        elif key == 'a': # Turn Left (Yaw)
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
    標準策略 (Standard / FPS Mode)
    ------------------------------
    這個策略會定義一個「軌道軸 (Orbit Axis)」，通常是 (0, 1, 0)。
    蛇在平面移動時，頭頂 (Up) 會鎖定這個軸，只有在爬牆時才會改變。
    """
    def __init__(self, snake):
        super().__init__(snake)
        # 定義 Orbital Camera 圍繞的軸 (預設為 Y 軸)
        # 這將作為模型在標準移動時的「世界上方」
        self.orbit_axis = Vec3(0, 1, 0)
        
        # 初始化參考向量 (需與 orbit_axis 垂直)
        self.horizontal_right_ref = Vec3(1, 0, 0)
        self.horizontal_forward_ref = Vec3(0, 0, 1)

    def handle_turn(self, key):
        snake = self.snake
        current_dir = snake.direction
        
        # 使用定義好的 Orbit Axis 作為世界座標的 Up
        world_up = self.orbit_axis
        world_down = -world_up
        
        right = current_dir.cross(snake.up)
        if right.length() < 0.01: right = self.horizontal_right_ref # 使用記憶的參考值防止萬向鎖
        right = right.normalized()
        
        new_direction = current_dir
        new_up = snake.up
        
        # 判斷是否垂直於軌道軸 (例如是否在爬牆)
        # 使用 dot product: 如果接近 1 或 -1，表示方向平行於 orbit_axis
        is_vertical = abs(current_dir.dot(world_up)) > 0.99

        if key in ('a', 'd'):
            if not is_vertical:
                if key == 'd': new_direction = -right
                else:          new_direction = right

                # 判斷新方向是否為「水平」(即垂直於 orbit_axis)
                # 如果是，強制將 Up 向量修正為 orbit_axis，確保頭頂朝向軌道軸
                if abs(new_direction.dot(world_up)) < 0.01:
                    new_up = world_up
                    self.horizontal_right_ref = right
                    self.horizontal_forward_ref = new_direction.normalized()
            else:
                # 垂直移動時 (爬牆中)，繞著自身的軸轉
                # 需要計算一個相對於世界的右向量
                ref_right = self.horizontal_forward_ref.cross(world_up).normalized()
                if key == 'd': new_direction = -ref_right.normalized()
                else:          new_direction = ref_right.normalized()
                new_up = world_up
                
                # [FIXED] 關鍵修正：
                # 當從垂直移動轉回水平移動時 (例如: 低頭時按 A/D)，
                # 必須更新水平參考向量，否則下次抬頭/低頭會依據舊方向旋轉，導致頭頂方向錯亂。
                self.horizontal_forward_ref = new_direction.normalized()
                self.horizontal_right_ref = new_direction.cross(world_up).normalized()

        elif key == 'w': # Pitch Up
            if current_dir != world_up and current_dir != world_down:
                new_direction = world_up
                new_up = self.horizontal_forward_ref
        
        elif key == 's': # Pitch Down
            if current_dir != world_up and current_dir != world_down:
                new_direction = world_down
                new_up = self.horizontal_forward_ref

        if new_direction.length() > 0.01 and new_direction != -current_dir:
            snake.direction = new_direction.normalized()
            snake.up = new_up.normalized()


# ==========================================
# 2. Snake Entity
# ==========================================

class Snake:
    def __init__(self):
        self.body = [
            Entity(model=SNAKE_BODY_MODLE, color=SNAKE_COLOR, scale=SNAKE_BODY_SCALE, position=(0, 0, 0), collider=None),
            Entity(model=SNAKE_BODY_MODLE, color=SNAKE_COLOR, scale=SNAKE_BODY_SCALE, position=(0, -1, 0), collider=None),
            Entity(model=SNAKE_BODY_MODLE, color=SNAKE_COLOR, scale=SNAKE_BODY_SCALE, position=(0, -2, 0), collider=None)
        ]
        self.head = self.body[0]
        
        # 1. Create a PIVOT Entity (Invisible Container)
        self.head_model = Entity(
            position=self.head.position
        )
        
        # 2. Create the VISUAL Mesh (The Skin)
        # 修正模型朝向：Red(X)+180, Blue(Z)+90 (保留使用者提供的設定)
        self.head_mesh = Entity(
            parent=self.head_model,
            model=SNAKE_HEAD_MODLE,                    
            scale=SNAKE_HEAD_SCALE,
            rotation_z=180, 
            rotation_y=270   
        )
        
        self.direction = Vec3(0, 1, 0) 
        self.up = Vec3(0, 0, 1)
        
        self.last_move_time = time.time()
        self.turn_buffer = []
        
        self.strategies = {
            'free_roam': FreeRoamStrategy(self), 
            'standard': StandardStrategy(self)   
        }
        self.current_strategy = self.strategies['free_roam']

        # --- ENABLE DEBUG AXES ---
        create_debug_axes(self.head_model, scale=2.5)

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
            print(f"4. Model Fwd    : {fmt(self.head_model.forward)}") 
            print(f"5. Model Up     : {fmt(self.head_model.up)}")
        print("----------------")

    def _apply_model_orientation_and_offset(self):
        if not self.head_model: return
        
        # 1. Sync Position
        self.head_model.position = self.head.position
        
        # 2. Delegate Rotation to Strategy
        self.current_strategy.update_model_orientation(self.head_model)
        
        # 3. Position Offset (Nudge forward slightly)
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
        new_segment = Entity(model=SNAKE_BODY_MODLE, color=SNAKE_COLOR, scale=SNAKE_BODY_SCALE, position=self.body[-1].position, collider=None)
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
