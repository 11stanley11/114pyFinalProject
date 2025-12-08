"""
Camera logic for following the snake in 3D space.
"""

from ursina import Entity, camera, lerp, time, Vec3

class SnakeCamera(Entity):
    def __init__(self, snake):
        super().__init__()
        self.snake = snake
        
        # 1. Settings
        camera.orthographic = False
        camera.fov = 90  # Wider FOV reduces motion sickness
        self.smooth_speed = 4  # How fast camera catches up (Higher = Snappier)
        self.distance = 14     # How far behind the snake
        self.height = 5        # How high above the snake
        self.offset_side = 3   # Lateral offset for 3D effect

        # 2. Snap to initial position immediately
        if self.snake and self.snake.head:
            self.update_camera_position(speed=100)

    def update(self):
        if not self.snake or not self.snake.head:
            return
            
        # Update every frame with smoothing
        self.update_camera_position(speed=time.dt * self.smooth_speed)

    def update_camera_position(self, speed):
        # --- 1. Calculate Target Position ---
        # We want to be behind (-direction) and above (+up) the snake
        
        # Ensure we have normalized vectors to prevent math errors
        direction = self.snake.direction.normalized()
        up = self.snake.up.normalized()
        right = direction.cross(up).normalized()

        # Base ideal spot (Center)
        base_pos = self.snake.head.position - (direction * self.distance) + (up * self.height)
        
        # Calculate two potential positions: Left and Right offsets
        target_left = base_pos - (right * self.offset_side)
        target_right = base_pos + (right * self.offset_side)
        
        # Dynamic Smoothness: Choose the side closer to the CURRENT camera position.
        dist_left = (camera.position - target_left).length()
        dist_right = (camera.position - target_right).length()
        
        target_pos = target_left if dist_left < dist_right else target_right

        # --- 2. Move Camera ---
        # Smoothly interpolate current position to target position
        camera.position = lerp(camera.position, target_pos, speed)
        
        # --- 3. Rotate Camera ---
        # Look at the snake's head, but CRUCIALLY:
        # We must also align the camera's "up" with the snake's "up".
        # This ensures the world spins around you, keeping controls intuitive.
        camera.lookAt(self.snake.head.position, up)