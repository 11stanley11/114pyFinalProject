"""
Camera logic for following the snake in 3D space
Now supports multiple camera modes (Orbital, TopDown, Follow).
"""

from ursina import Entity, camera, lerp, time, Vec3, scene, window
import math

# --- 1. Base Class ---
class CameraMode(Entity):
    def __init__(self, snake, **kwargs):
        super().__init__(**kwargs)
        self.snake = snake
        self.active = False
        
        if self.snake:
            self.last_valid_direction = self.snake.direction.normalized()
            self.last_valid_up = self.snake.up.normalized()
        else:
            self.last_valid_direction = Vec3(0, 0, 1)
            self.last_valid_up = Vec3(0, 1, 0)
            
        camera.orthographic = False

    def enable(self):
        self.active = True
        if camera.parent != scene:
            camera.parent = scene
        self._update_valid_vectors()

    def disable(self):
        self.active = False

    def _update_valid_vectors(self):
        if not self.snake: return
        if self.snake.direction.length() > 0.01:
            self.last_valid_direction = self.snake.direction.normalized()
        if self.snake.up.length() > 0.01:
            self.last_valid_up = self.snake.up.normalized()

    def update(self):
        if self.active:
            self._update_valid_vectors()

# --- 2. Modes ---

class OrbitalCameraMode(CameraMode):
    """
    Mode: Orbital / Tracking
    Rotates around the center of the grid.
    Paired with: Standard Input.
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

    def _target_info(self):
        az = self._azimuth_from_head()
        cam_x = self.center.x + self.radius * math.cos(az)
        cam_z = self.center.z + self.radius * math.sin(az)
        cam_y = self.snake.head.position.y + self.height 
        return Vec3(cam_x, cam_y, cam_z), self.snake.head.position

    def enable(self):
        super().enable()
        camera.fov = 90
        if self.snake.head: 
            pos, look = self._target_info()
            camera.position = pos
            camera.look_at(look) 
            camera.rotation_z = 0

    def update(self):
        super().update()
        if not self.active or not self.snake or not self.snake.head: return
        target_pos, look_point = self._target_info()
        camera.position = lerp(camera.position, target_pos, time.dt * self.smooth)
        camera.look_at(look_point, axis='forward', up=Vec3(0,1,0))
        camera.rotation_z = 0


class TopDownCameraMode(CameraMode):
    """
    Mode: Top Down
    Looking down from above.
    Paired with: Standard Input.
    """
    def __init__(self, snake, **kwargs):
        super().__init__(snake, **kwargs)
        self.distance = 14.0 
        self.height = 10.0   
        self.smooth = 10
        
    def _target_info(self):
        # Always use the last valid direction to avoid camera snapping when stopped
        direction = self.last_valid_direction
            
        target_pos = self.snake.head.position - (direction * self.distance) + Vec3(0, self.height, 0)
        look_point = self.snake.head.position
        return target_pos, look_point

    def enable(self):
        super().enable()
        camera.fov = 90
        if self.snake.head:
            pos, look = self._target_info()
            camera.position = pos
            camera.look_at(look)
        
    def update(self):
        super().update()
        if not self.active or not self.snake or not self.snake.head: return
        
        target_pos, look_point = self._target_info()
        
        camera.position = lerp(camera.position, target_pos, time.dt * self.smooth)
        # Force 'up' to be World Up for stable top-down view
        camera.look_at(look_point, axis='forward', up=Vec3(0,1,0))
        camera.rotation_z = 0 


class FollowCameraMode(CameraMode):
    """
    Mode: Follow / Action (Classic)
    Your original camera logic.
    Paired with: Free Roam Input.
    """
    def __init__(self, snake, **kwargs):
        super().__init__(snake, **kwargs)
        self.smooth_speed = 4
        self.distance = 14
        self.height = 5
        self.offset_side = 3

    def enable(self):
        super().enable()
        camera.fov = 90
        # Instant rotate, smooth zoom (speed=0 for orientation only)
        if self.snake.head:
            self._update_cam(speed=0)

    def update(self):
        super().update()
        if not self.active or not self.snake or not self.snake.head: return
        self._update_cam(speed=time.dt * self.smooth_speed)

    def _update_cam(self, speed):
        direction = self.last_valid_direction
        up = self.last_valid_up
        right = direction.cross(up).normalized()

        base_pos = self.snake.head.position - (direction * self.distance) + (up * self.height)
        
        target_left = base_pos - (right * self.offset_side)
        target_right = base_pos + (right * self.offset_side)
        
        dist_left = (camera.position - target_left).length()
        dist_right = (camera.position - target_right).length()
        
        target_pos = target_left if dist_left < dist_right else target_right

        camera.position = lerp(camera.position, target_pos, speed)
        camera.lookAt(self.snake.head.position, up)


# --- 3. Manager ---

class SnakeCamera(Entity):
    def __init__(self, snake, grid_center=Vec3(0,0,0)):
        super().__init__()
        self.snake = snake
        
        self.modes = {
            'orbital': OrbitalCameraMode(snake, grid_center),
            'topdown': TopDownCameraMode(snake),
            'follow': FollowCameraMode(snake)
        }
        
        self.current_mode_name = 'follow'
        
        for mode in self.modes.values():
            mode.disable()
            
        self.set_mode(self.current_mode_name)

    def set_mode(self, name):
        if name in self.modes:
            if self.current_mode_name:
                self.modes[self.current_mode_name].disable()
            
            self.current_mode_name = name
            self.modes[name].enable()

    def input(self, key):
        pass
