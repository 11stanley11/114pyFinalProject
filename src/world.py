"""
The game world, including the grid.
"""

from ursina import Entity, Pipe, Vec3, color
from config import GRID_SIZE, GRID_COLOR, BOUNDARY_COLOR

class WorldGrid(Entity):
    def __init__(self):
        super().__init__()
        
        half_grid = GRID_SIZE // 2
        joint_size = 0.075

        # --- Draw Boundary Planes ---
        boundary_plane_alpha = 0.1 # Semi-transparent
        
        # X-planes
        Entity(parent=self, model='cube', scale=(0.1, GRID_SIZE + 1, GRID_SIZE + 1), position=(half_grid + 0.5, 0, 0), color=BOUNDARY_COLOR, alpha=boundary_plane_alpha)
        Entity(parent=self, model='cube', scale=(0.1, GRID_SIZE + 1, GRID_SIZE + 1), position=(-half_grid - 0.5, 0, 0), color=BOUNDARY_COLOR, alpha=boundary_plane_alpha)
        
        # Y-planes
        Entity(parent=self, model='cube', scale=(GRID_SIZE + 1, 0.1, GRID_SIZE + 1), position=(0, half_grid + 0.5, 0), color=BOUNDARY_COLOR, alpha=boundary_plane_alpha)
        Entity(parent=self, model='cube', scale=(GRID_SIZE + 1, 0.1, GRID_SIZE + 1), position=(0, -half_grid - 0.5, 0), color=BOUNDARY_COLOR, alpha=boundary_plane_alpha)
        
        # Z-planes
        Entity(parent=self, model='cube', scale=(GRID_SIZE + 1, GRID_SIZE + 1, 0.1), position=(0, 0, half_grid + 0.5), color=BOUNDARY_COLOR, alpha=boundary_plane_alpha)
        Entity(parent=self, model='cube', scale=(GRID_SIZE + 1, GRID_SIZE + 1, 0.1), position=(0, 0, -half_grid - 0.5), color=BOUNDARY_COLOR, alpha=boundary_plane_alpha)


        # --- Draw Grid Joints with Gradient and Transparency ---
        max_dist = Vec3(half_grid, half_grid, half_grid).length()

        for x in range(-half_grid, half_grid + 1):
            for y in range(-half_grid, half_grid + 1):
                for z in range(-half_grid, half_grid + 1):
                    position = Vec3(x, y, z)
                    dist = position.length()
                    
                    if max_dist > 0:
                        norm_dist = dist / max_dist
                    else:
                        norm_dist = 0

                    # Alpha: closer is more opaque
                    alpha = 1 - (norm_dist * 0.8)
                    
                    # Brightness: closer is brighter
                    brightness = 1 - (norm_dist * 0.5)
                    
                    joint_color = color.Color(GRID_COLOR.r * brightness, 
                                              GRID_COLOR.g * brightness, 
                                              GRID_COLOR.b * brightness, 
                                              alpha)

                    Entity(parent=self, model='sphere', color=joint_color, scale=joint_size, position=position)
        
        # Optimize: Combine all children into one mesh to reduce draw calls
        self.combine()
