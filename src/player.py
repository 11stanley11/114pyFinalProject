"""
The player-controlled snake.
"""

from ursina import Entity, Vec3, color, Vec4
import time
from config import SNAKE_SPEED, SNAKE_COLOR, GRID_SIZE

class Snake:
    def __init__(self):
        # 修正：初始位置應沿 Y 軸排列 (Y軸為中心軸/向上方向)
        self.body = [
            Entity(model='cube', color=SNAKE_COLOR, scale=1, position=(0, 0, 0)),
            Entity(model='cube', color=SNAKE_COLOR, scale=1, position=(0, -1, 0)), # 沿 Y 軸負向延伸
            Entity(model='cube', color=SNAKE_COLOR, scale=1, position=(0, -2, 0))
        ]
        self.head = self.body[0]
        self.head_marker = Entity(model='cube', color=color.yellow, scale=(0.5, 0.1, 0.5))
        # 修正：初始方向沿 Y 軸正向
        self.direction = Vec3(0, 1, 0)  
        # 修正：初始 Up 向量設為 Z 軸 (與新的 Direction (Y) 正交)
        self.up = Vec3(0, 0, 1) 
        # 儲存上一次水平移動時的「右」向量，用於在垂直移動時定義 A/D 的方向記憶
        self.horizontal_right_ref = Vec3(1, 0, 0) 
        # 新增：儲存上一次水平移動時的「前進」向量 (用於垂直狀態下的 A/D 轉向)
        self.horizontal_forward_ref = Vec3(0, 0, 1) # 初始設定為 Z 軸
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
            
            # Calculate the 'right' vector based on current direction and up vector (Always orthogonal)
            right = self.direction.cross(self.up).normalized()
            
            new_direction = self.direction
            new_up = self.up
            
            # 世界向上方向 (Y 軸)
            world_up_dir = Vec3(0, 1, 0) 
            world_down_dir = Vec3(0, -1, 0) # 世界向下方向 (負Y 軸)

            # 判斷當前是否處於垂直移動狀態 (Y 軸分量接近 +/- 1)
            is_currently_vertical = abs(self.direction.y) > 0.99

            # --- Yaw (A/D) ---
            if key == 'd' or key == 'a':
                
                if not is_currently_vertical:
                    # ** Case 1: Horizontal/Diagonal movement (Normal turn) **
                    
                    if key == 'd': # Turn Left (relative to current direction)
                        new_direction = -right
                    else: # key == 'a' # Turn Right (relative to current direction)
                        new_direction = right

                    # *** A/D 修正: 穩定化 Up 向量 ***
                    if abs(new_direction.y) < 0.01:
                        new_up = world_up_dir
                        
                    # ** 關鍵更新: 如果新的方向是水平的，更新水平記憶 **
                    if abs(new_direction.y) < 0.01:
                        # 儲存當前轉向時的 'right' 向量作為水平轉向的參考
                        self.horizontal_right_ref = right 
                        # 儲存當前轉向時的 'forward' 向量作為水平轉向的參考
                        self.horizontal_forward_ref = new_direction.normalized()
                    else:
                        new_up = self.up
                        
                else: 
                    # ** Case 2: Vertical movement (使用記憶的 A/D 轉向) **
                    
                    # 計算記憶中前進方向的 '右' 向量（垂直於 forward_ref 和世界 Up 向量）
                    ref_right = self.horizontal_forward_ref.cross(world_up_dir).normalized()
                    
                    # D (Left Turn): 轉向記憶中 '前進' 向量的右方負方向
                    if key == 'd':
                        new_direction = -ref_right.normalized()
                    # A (Right Turn): 轉向記憶中 '前進' 向量的右方正方向
                    else: # key == 'a'
                        new_direction = ref_right.normalized()
                        
                    # 轉回水平平面後，必須將 Up 向量重設為世界 Up (Y 軸)
                    new_up = world_up_dir
                
            # --- Pitch (W/S) ---
            elif key == 'w': # Turn Up (絕對世界向上)
                # 關鍵修正：如果已經面朝世界向上，則不改變方向
                if self.direction.normalized() == world_up_dir:
                    return 
                
                # 如果新方向與舊方向完全相反 (180度轉彎)，則不執行 (避免立即碰撞)
                if self.direction.normalized() != -world_up_dir:
                    new_direction = world_up_dir
                    # 當轉向世界向上 (Y軸) 時，新的 Up 向量設為 Z 軸 (維持 Roll 鎖定)
                    new_up = Vec3(0, 0, 1)

            elif key == 's': # Turn Down (絕對世界向下)
                # 關鍵修正：如果已經面朝世界向下，則不改變方向
                if self.direction.normalized() == world_down_dir:
                    return 
                
                # 如果新方向與舊方向完全相反 (180度轉彎)，則不執行 (避免立即碰撞)
                if self.direction.normalized() != -world_down_dir:
                    new_direction = world_down_dir
                    # 當轉向世界向下 (負Y軸) 時，新的 Up 向量設為 Z 軸 (維持 Roll 鎖定)
                    new_up = Vec3(0, 0, 1)
                
            # --- Application of new direction ---
            # 1. 確保不是 180 度轉向
            if new_direction.normalized() != -self.direction.normalized():
                self.direction = new_direction.normalized()
                self.up = new_up.normalized() 

    def will_collide(self, grid_size):
        """
        Checks if the snake will collide with walls or itself on its next move.
        """
        next_head_position = self.head.position + self.direction.normalized()
        half_grid = grid_size // 2

        # Wall collision
        # 修正：檢查 X, Y, Z 三軸的牆壁碰撞
        if (next_head_position.x > half_grid or next_head_position.x < -half_grid or 
            next_head_position.y > half_grid or next_head_position.y < -half_grid or 
            next_head_position.z > half_grid or next_head_position.z < -half_grid):
            return True

        # Self collision (only check against body segments, excluding the head itself)
        for segment in self.body[1:]:
            if next_head_position == segment.position:
                return True

        return False

    def move(self):
        # --- Move body ---
        # The last segment moves to the position of the second to last, and so on.
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].position = self.body[i - 1].position

        # --- Move head ---
        self.head.position += self.direction.normalized()

        # --- Update head marker (Visual Rotation) ---
        # Position marker slightly above/along the snake's up vector
        self.head_marker.position = self.head.position + self.up * 0.5
        
        # Set the marker's up direction
        self.head_marker.world_up = self.up
        
        # Make the marker look in the direction of movement
        self.head_marker.look_at(self.head.position + self.direction)


    def grow(self):
        new_segment = Entity(model='cube', color=SNAKE_COLOR, scale=1, position=self.body[-1].position)
        self.body.append(new_segment)
        self.update_appearance()