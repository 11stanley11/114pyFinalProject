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

        # Calculate the ideal spot
        target_pos = self.snake.head.position - (direction * self.distance) + (up * self.height)

        # --- 2. Move Camera ---
        # Smoothly interpolate current position to target position
        camera.position = lerp(camera.position, target_pos, speed)
        
        # --- 3. Rotate Camera ---
        # Look at the snake's head, but CRUCIALLY:
        # We must also align the camera's "up" with the snake's "up".
        # This ensures the world spins around you, keeping controls intuitive.
        camera.look_at(self.snake.head.position, axis='forward', up=up)