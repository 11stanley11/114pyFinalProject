"""
The game world, including the grid.
"""

from ursina import Entity, Pipe, Vec3, color, destroy
import config
from config import GRID_COLOR, BOUNDARY_COLOR

class WorldGrid(Entity):
    def __init__(self):
        super().__init__()
        
        self.shells = []
        self.boundary_planes = []
        
        # We'll use MAX_GRID_SIZE to generate all possible points once
        max_half_grid = config.MAX_GRID_SIZE // 2
        joint_size = 0.075
        
        # --- 1. Pre-generate Grid Shells ---
        # Shell 0 is just the center point (0,0,0)
        # Shell R contains points where max(|x|,|y|,|z|) == R
        
        # For coloring, we use the max radius as reference so the gradient is consistent
        max_dist_ref = Vec3(max_half_grid, max_half_grid, max_half_grid).length()

        for r in range(max_half_grid + 1):
            shell_parent = Entity(parent=self)
            
            # Optimization: If r=0, just one point
            if r == 0:
                points_to_check = [(0,0,0)]
            else:
                # We need all (x,y,z) such that max(|x|,|y|,|z|) == r
                points_to_check = []
                for x in range(-r, r + 1):
                    for y in range(-r, r + 1):
                        for z in range(-r, r + 1):
                            if max(abs(x), abs(y), abs(z)) == r:
                                points_to_check.append((x,y,z))

            for (x,y,z) in points_to_check:
                position = Vec3(x, y, z)
                dist = position.length()
                
                if max_dist_ref > 0:
                    norm_dist = dist / max_dist_ref
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

                Entity(parent=shell_parent, model='sphere', color=joint_color, scale=joint_size, position=position)
            
            # Combine this shell into one mesh
            shell_parent.combine()
            shell_parent.enabled = False # Hide initially
            self.shells.append(shell_parent)

        # --- 2. Create Boundary Planes (Mutable) ---
        # We create them once and just move/scale them in set_size
        boundary_plane_alpha = 0.1
        
        # Store them in a list or dict. 
        # Order: +X, -X, +Y, -Y, +Z, -Z
        for i in range(6):
            bp = Entity(parent=self, model='cube', color=BOUNDARY_COLOR, alpha=boundary_plane_alpha)
            self.boundary_planes.append(bp)

        # Initialize with default size
        self.set_size(config.GRID_SIZE)

    def set_size(self, size):
        half_grid = size // 2
        
        # 1. Update Shell Visibility
        # Enable shells 0 to half_grid
        for r, shell in enumerate(self.shells):
            if r <= half_grid:
                shell.enabled = True
            else:
                shell.enabled = False
                
        # 2. Update Boundary Planes
        # Scale: One dimension is 0.1 (thickness), others are size+1
        thick = 0.1
        span = size + 1
        offset = half_grid + 0.5
        
        # +X
        self.boundary_planes[0].scale = (thick, span, span)
        self.boundary_planes[0].position = (offset, 0, 0)
        
        # -X
        self.boundary_planes[1].scale = (thick, span, span)
        self.boundary_planes[1].position = (-offset, 0, 0)
        
        # +Y
        self.boundary_planes[2].scale = (span, thick, span)
        self.boundary_planes[2].position = (0, offset, 0)
        
        # -Y
        self.boundary_planes[3].scale = (span, thick, span)
        self.boundary_planes[3].position = (0, -offset, 0)
        
        # +Z
        self.boundary_planes[4].scale = (span, span, thick)
        self.boundary_planes[4].position = (0, 0, offset)
        
        # -Z
        self.boundary_planes[5].scale = (span, span, thick)
        self.boundary_planes[5].position = (0, 0, -offset)