from ursina import camera, Vec3, lerp, time, Entity, Text, color, scene, window
import math

# --- 1. 攝影機模式基礎類別 ---

class CameraMode(Entity):
    """攝影機模式的基礎類別"""
    def __init__(self, snake, **kwargs):
        super().__init__(**kwargs) 
        self.snake = snake
        self.active = False
        self.enabled = False 
        
        # 儲存上一次有效的方向，避免蛇停止時向量歸零
        self.last_valid_direction = Vec3(0, 0, 1)
        self.last_valid_up = Vec3(0, 1, 0)

        camera.orthographic = False
        
    def enable(self):
        self.active = True
        self.enabled = True 
        if camera.parent != scene:
            camera.parent = scene 
        # 重置最後有效方向
        if self.snake and self.snake.head:
            self._update_valid_vectors()

    def disable(self):
        self.active = False
        self.enabled = False

    def _update_valid_vectors(self):
        """更新並驗證方向向量，確保不使用零向量"""
        if not self.snake: return

        # 檢查方向向量長度
        curr_dir = self.snake.direction
        if curr_dir.length() > 0.01:
            self.last_valid_direction = curr_dir.normalized()
        
        # 檢查 Up 向量
        curr_up = self.snake.up
        if curr_up.length() > 0.01:
            self.last_valid_up = curr_up.normalized()

    def update(self):
        if self.active:
            self._update_valid_vectors()

# --- 2. 攝影機模式實作 ---

class OriginalTrackingMode(CameraMode):
    """
    模式 1: 軌道追蹤 (Orbital)
    """
    def __init__(self, snake, grid_center=Vec3(0,0,0), **kwargs):
        super().__init__(snake, **kwargs)
        self.center = grid_center 
        self.radius = 20.0 
        self.height = 10.0 
        self.smooth = 5.0  
        self._current_az = 0.0 
        
    def _azimuth_from_head(self):
        rel = self.snake.head.position - self.center
        dist_sq = rel.x**2 + rel.z**2
        if dist_sq < 0.1: return self._current_az
        target_az = math.atan2(rel.z, rel.x)
        self._current_az = target_az 
        return target_az

    def _target_position_and_look(self):
        az = self._azimuth_from_head()
        cam_x = self.center.x + self.radius * math.cos(az)
        cam_z = self.center.z + self.radius * math.sin(az)
        cam_y = self.snake.head.position.y + self.height 
        return Vec3(cam_x, cam_y, cam_z), self.snake.head.position

    def enable(self):
        super().enable()
        if self.snake.head: 
            pos, look = self._target_position_and_look()
            camera.position = pos
            camera.look_at(look) 
            camera.rotation_z = 0

    def update(self):
        super().update() # 更新有效向量
        if not self.active or not self.snake or not self.snake.head: return
        target_pos, look_point = self._target_position_and_look()
        camera.position = lerp(camera.position, target_pos, time.dt * self.smooth)
        camera.look_at(look_point)
        camera.rotation_z = 0

class TopDownCameraMode(CameraMode):
    """
    模式 2:未完成/未啟用
    """
    def __init__(self, snake, **kwargs):
        super().__init__(snake, **kwargs)
        self.distance = 14.0 
        self.height = 10.0   
        self.smooth = 10
        
    def _target_info(self):
        direction = self.last_valid_direction
            
        # 目標位置
        target_pos = self.snake.head.position - (direction * self.distance) + Vec3(0, self.height, 0)
        
        # 看向點
        look_point = self.snake.head.position
        return target_pos, look_point

    def enable(self):
        super().enable()
        if self.snake.head:
            pos, look = self._target_info()
            camera.position = pos
            camera.look_at(look)
        
    def update(self):
        super().update()
        if not self.active or not self.snake or not self.snake.head: return
        
        target_pos, look_point = self._target_info()
        
        camera.position = lerp(camera.position, target_pos, time.dt * self.smooth)
        camera.look_at(look_point, axis='forward', up=Vec3(0,1,0))
        camera.rotation_z = 0 

class FirstPersonCameraMode(CameraMode):
    """
    模式 3: 貼身視角 (Follow / Action Cam)
    """
    def __init__(self, snake,**kwargs):
        super().__init__(snake, **kwargs)
        camera.fov = 80 

    def update(self):
        super().update()
        if not self.active or not self.snake or not self.snake.head: return

        forward = self.last_valid_direction
        up = self.last_valid_up
        
        # 計算側向向量

        # 這裡加入檢查，如果平行則使用默認 Right
        try:
            side_raw = up.cross(forward)
            if side_raw.length() < 0.01:
                side = Vec3(1,0,0) # 默認右邊
            else:
                side = side_raw.normalized()
        except:
            side = Vec3(1,0,0)

        # 目標位置：蛇頭後方 + 上方
        offset = -forward * 8 + up * 10
        
        desired_position = self.snake.head.position + offset
        
        camera.position = lerp(camera.position, desired_position, time.dt * 6)
        
        # 看向前方遠處
        look_target = self.snake.head.position + forward * 5
        camera.look_at(look_target)

# --- 3. 攝影機管理器 ---

class SnakeCamera(Entity):
    def __init__(self, snake, grid_center=Vec3(0,0,0)):
        super().__init__()
        self.snake = snake
        
        self.mode_list = [
            OriginalTrackingMode(snake, grid_center=grid_center), # Index 0
            FirstPersonCameraMode(snake)# Index 1                   
        ]
        self.current_mode_index = 1
        
        self.help_text = Text(
            text="", position=Vec3(window.top_left.x + 0.05, window.top_left.y - 0.1), 
            scale=1.5, color=color.white, enabled=False, parent=camera.ui
        )

        # 初始設定
        for mode in self.mode_list:
            mode.disable()
            
        self.set_mode(0)
        self.update_ui()

    def set_mode(self, index):
        """切換到指定索引的模式"""
        self.mode_list[self.current_mode_index].disable()
        self.current_mode_index = index % len(self.mode_list)
        new_mode = self.mode_list[self.current_mode_index]
        new_mode.enable()
        self.update_ui()

    def cycle_mode(self):
        """循環切換下一個模式"""
        self.set_mode(self.current_mode_index + 1)

    def update_ui(self):
        mode_name = self.mode_list[self.current_mode_index].__class__.__name__.replace('Mode', '')
        if self.help_text:
            self.help_text.text = f"Cam Mode: {mode_name}\n[RD] / [C] to Change View"
            self.help_text.enabled = True

    def input(self, key):
        if key == 'gamepad right shoulder' or key == 'gamepad left shoulder' or key == 'c':
            self.cycle_mode()