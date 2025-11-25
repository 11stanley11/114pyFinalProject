"""
Camera logic for following the snake.
"""

from ursina import Entity, camera, lerp, time, Vec3

class SnakeCamera(Entity):
    def __init__(self, snake):
        super().__init__()
        self.snake = snake
        camera.orthographic = False
        camera.fov = 75

    def update(self):
        if self.snake and self.snake.body:
            # Calculate side vector
            side = self.snake.up.cross(self.snake.direction).normalized()

            # Desired position is behind, above, and to the side of the snake's head
            offset = -self.snake.direction.normalized() * 15 + self.snake.up.normalized() * 5 + side * 5
            desired_position = self.snake.head.position + offset
            
            # Smoothly move the camera to the desired position
            camera.position = lerp(camera.position, desired_position, time.dt * 4)
            
            # Always look at the snake's head
            camera.look_at(self.snake.head.position)
