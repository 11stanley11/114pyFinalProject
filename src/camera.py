from ursina import camera, Vec3, lerp, time, Entity # 引入 Entity
import math

class SnakeCamera(Entity):
    """
    軌道追蹤攝影機 (Orbital Tracking Camera) - 最終修正版。
    鏡頭繞著 grid_center (Y軸) 旋轉，追蹤蛇頭的位置。
    視角鎖定在蛇頭在地面上的投影點 (Y=center.y)，以確保世界中心的 Y 軸始終位於畫面中心附近。
    """
    def __init__(self, snake, grid_center=Vec3(0,0,0)):
        super().__init__()
        self.snake   = snake
        self.center  = grid_center # 世界網格的中心點 (Y=0)
        
        self.radius  = 20.0  # 鏡頭的水平半徑 (可以調整)
        self.height  = 15.0  # 鏡頭的高度 (+Y) (可以調整)
        self.smooth  = 5.0   # 平滑追蹤速度
        
        # 追蹤當前角度，用於防止蛇頭在中心點時角度亂跳
        self._current_az = 0.0 
        self._snap_to_target()

    def _azimuth_from_head(self):
        """計算「中心 → 蛇頭」的向量所決定的方位角，決定鏡頭的旋轉角度。"""
        rel = self.snake.head.position - self.center
        dist_sq = rel.x**2 + rel.z**2
        
        # 優化：防止蛇頭到達中心點時 (dist_sq ≈ 0) 角度計算錯誤導致鏡頭抖動
        if dist_sq < 0.1: 
            return self._current_az
        
        target_az = math.atan2(rel.z, rel.x)
        self._current_az = target_az 
        return target_az

    def _target_position_and_look(self):
        """計算攝影機的目標位置和視線點。"""
        az = self._azimuth_from_head()

        # 1. 鏡頭位置：繞中心的圓周 (實現鏡頭繞 Y 軸跟隨)
        cam_x = self.center.x + self.radius * math.cos(az)
        cam_z = self.center.z + self.radius * math.sin(az)
        cam_y = self.center.y + self.height
        target_pos = Vec3(cam_x, cam_y, cam_z)

        # 2. 鏡頭視線點 (Look Point)
        # 關鍵修正：將視線點的 Y 軸固定在中心點的 Y 軸高度 (假設 Y=0 是地面或中心)。
        # 這樣鏡頭會略微向下傾斜，確保中央 Y 軸保持在視野中。
        look_point_x = self.snake.head.position.x
        look_point_z = self.snake.head.position.z
        look_point_y = self.center.y # 鎖定視線 Y 軸
        
        look_point = Vec3(look_point_x, look_point_y, look_point_z)
        
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
        # 這是確保 Y 軸「直的」最可靠的 Ursina 兼容方法。
        camera.rotation_z = 0