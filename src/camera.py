from ursina import camera, Vec3, lerp, time, Entity # 引入 Entity
import math

class SnakeCamera(Entity):
    """
    軌道追蹤攝影機 (Orbital Tracking Camera)。
    鏡頭繞著 grid_center (Y軸) 旋轉，追蹤蛇頭的位置。
    鏡頭和視線點的高度現在會跟隨蛇頭 Y 座標移動，確保蛇在 3D 空間中始終位於畫面中心。
    """
    def __init__(self, snake, grid_center=Vec3(0,0,0)):
        super().__init__()
        self.snake   = snake
        # 修正：世界網格的中心點 (Y=0)
        self.center  = grid_center 
        
        self.radius  = 20.0  # 鏡頭的水平半徑 (可以調整)
        self.height  = 10.0  # 鏡頭相對蛇頭的 Y 軸高度差 (+Y) (可以調整)
        self.smooth  = 5.0   # 平滑追蹤速度
        
        # 追蹤當前角度，用於防止蛇頭在中心點時角度亂跳
        self._current_az = 0.0 
        self._snap_to_target()

    def _azimuth_from_head(self):
        """計算「中心 → 蛇頭」在 X-Z 平面上的向量所決定的方位角，決定鏡頭的旋轉角度。"""
        # 修正：使用 X 和 Z 分量計算平面旋轉
        rel = self.snake.head.position - self.center
        dist_sq = rel.x**2 + rel.z**2
        
        # 優化：防止蛇頭到達中心點時 (dist_sq ≈ 0) 角度計算錯誤導致鏡頭抖動
        if dist_sq < 0.1: 
            return self._current_az
        
        # 修正：使用 atan2(Z, X) 計算方位角 (繞 Y 軸旋轉)
        target_az = math.atan2(rel.z, rel.x)
        self._current_az = target_az 
        return target_az

    def _target_position_and_look(self):
        """計算攝影機的目標位置和視線點。"""
        az = self._azimuth_from_head()

        # --- 1. 計算鏡頭位置 (追蹤蛇頭的 Y 軸高度) ---
        # 鏡頭位置：繞中心的圓周 (實現鏡頭繞 Y 軸跟隨)
        # 修正：旋轉發生在 X-Z 平面
        cam_x = self.center.x + self.radius * math.cos(az)
        cam_z = self.center.z + self.radius * math.sin(az)
        # 關鍵修正：鏡頭的高度現在跟著蛇頭的 Y 座標移動，保持固定的高度差 (self.height)。
        cam_y = self.snake.head.position.y + self.height 
        target_pos = Vec3(cam_x, cam_y, cam_z)

        # --- 2. 鏡頭視線點 (Look Point) ---
        # 修正：視線點直接看向蛇頭的當前位置，確保蛇在 Y 軸上不會偏離畫面中心。
        look_point = self.snake.head.position
        
        return target_pos, look_point

    def _snap_to_target(self):
        """遊戲開始時瞬間定位鏡頭。"""
        pos, look = self._target_position_and_look()
        camera.position = pos
        # 修正：移除無效的 up=Vec3.up 參數
        camera.look_at(look) 
        # 修正：強制 Z 軸旋轉為 0，確保 Y 軸直立
        camera.rotation_z = 0

    def update(self):
        """每一幀平滑移動鏡頭。"""
        target_pos, look_point = self._target_position_and_look()
        
        # 平滑移動位置
        camera.position = lerp(camera.position, target_pos, time.dt * self.smooth)
        
        # 讓鏡頭看向目標視線點
        camera.look_at(look_point)
        
        # 關鍵修正：強制鏡頭的 Z 軸旋轉 (Roll) 始終為 0，鎖定 Y 軸垂直
        camera.rotation_z = 0