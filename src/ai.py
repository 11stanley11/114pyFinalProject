# Contains the AI class for computer-controlled snakes.
from ursina import Entity, Vec3, color, distance, destroy
import random
import time
from config import AI_COLOR, GRID_SIZE, AI_SPEED

class AISnake:
    def __init__(self, start_pos=(5, 0, 5), aggressive_mode=False):
        self.body = [
            Entity(model='cube', color=AI_COLOR, scale=1, position=start_pos),
            Entity(model='cube', color=AI_COLOR, scale=1, position=(start_pos[0], start_pos[1]-1, start_pos[2])),
            Entity(model='cube', color=AI_COLOR, scale=1, position=(start_pos[0], start_pos[1]-2, start_pos[2]))
        ]
        self.head = self.body[0]
        self.direction = Vec3(0, 1, 0)
        self.last_move_time = time.time()
        self.speed = AI_SPEED
        self.alive = True
        self.aggressive_mode = aggressive_mode
        self.hunt_radius = 6
        self.update_appearance()

    def update_appearance(self):
        num_segments = len(self.body)
        if num_segments <= 1:
            self.head.color = AI_COLOR
            return

        for i, segment in enumerate(self.body):
            alpha = 1.0 - (i / (num_segments - 1)) * 0.8
            segment.color = color.Color(AI_COLOR.r, AI_COLOR.g, AI_COLOR.b, alpha)

    def get_valid_moves(self, player_snake, grid_size):
        """
        Returns a list of vectors (directions) that won't kill the AI.
        """
        possible_moves = [
            Vec3(1,0,0), Vec3(-1,0,0), 
            Vec3(0,1,0), Vec3(0,-1,0), 
            Vec3(0,0,1), Vec3(0,0,-1)
        ]
        
        safe_moves = []
        half_grid = grid_size // 2

        for move in possible_moves:
            # Don't reverse direction instantly
            if move == -self.direction:
                continue

            next_pos = self.head.position + move
            
            # 1. Check Wall Collision
            if (next_pos.x > half_grid or next_pos.x < -half_grid or 
                next_pos.y > half_grid or next_pos.y < -half_grid or 
                next_pos.z > half_grid or next_pos.z < -half_grid):
                continue
            
            # 2. Check Self Collision
            hit_self = False
            for segment in self.body:
                if next_pos == segment.position:
                    hit_self = True
                    break
            if hit_self: continue

            # 3. Check Player Collision (Don't run into the player)
            hit_player = False
            for segment in player_snake.body:
                if next_pos == segment.position:
                    hit_player = True
                    break
            if hit_player: continue

            safe_moves.append(move)
            
        return safe_moves

    def decide_move(self, food, player_snake):
        if not self.alive: return

        # Only move if enough time passed
        if time.time() - self.last_move_time < 1 / self.speed:
            return

        self.last_move_time = time.time()

        # Get all moves that won't kill us immediately
        safe_moves = self.get_valid_moves(player_snake, GRID_SIZE)

        if not safe_moves:
            # No moves? AI dies or freezes.
            return

        # --- DYNAMIC STRATEGY SELECTION ---
        
        # 1. Calculate Distances
        dist_to_player = distance(self.head.position, player_snake.head.position)
        dist_to_food = distance(self.head.position, food.position)
        
        # 2. Calculate Priorities
        # Food Priority: Base urgency + proximity bonus
        food_priority = 10.0
        food_priority += 30.0 / (dist_to_food + 0.1)  # Increases sharply as we get closer to food
        if len(self.body) < len(player_snake.body):
            food_priority += 15.0 # Extra hungry if smaller than player

        # Hunt Priority: Only if aggressive
        hunt_priority = 0.0
        if self.aggressive_mode:
            hunt_priority = 12.0 # Base hunt desire
            hunt_priority += 25.0 / (dist_to_player + 0.1) # Increases as we get closer to prey
            
            # Confidence boost if larger
            if len(self.body) > len(player_snake.body):
                hunt_priority += 10.0
            
            # If food is practically adjacent, override hunting unless we are literally on top of player
            if dist_to_food < 2 and dist_to_player > 2:
                hunt_priority = 0

        # 3. Determine Target
        target_pos = food.position # Default
        mode = "EAT"

        if hunt_priority > food_priority:
            mode = "HUNT"
            # Improved Interception Logic
            # Instead of a fixed intercept, predict based on distance
            # If far, aim far ahead. If close, aim for the throat.
            prediction_steps = max(1, min(6, int(dist_to_player / 1.5)))
            
            # Project player's future position
            intercept_point = player_snake.head.position + (player_snake.direction * prediction_steps)
            target_pos = intercept_point
            
        # ---------------------------

        # Simple AI: Pick the move that minimizes distance to target
        best_move = safe_moves[0]
        min_dist = float('inf')

        # Shuffle safe moves so if distances are equal, it picks randomly 
        # (prevents getting stuck in loops)
        random.shuffle(safe_moves) 

        for move in safe_moves:
            next_pos = self.head.position + move
            dist_to_target = distance(next_pos, target_pos)
            
            # Tie-breaker: If hunting, try to stay close to the center to avoid getting trapped in corners
            if mode == "HUNT":
                dist_to_center = distance(next_pos, Vec3(0,0,0))
                dist_to_target += dist_to_center * 0.1 # Slight bias towards center

            if dist_to_target < min_dist:
                min_dist = dist_to_target
                best_move = move

        self.direction = best_move
        self.move()

    def move(self):
        # Move body segments
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].position = self.body[i - 1].position

        # Move head
        self.head.position += self.direction
        
        # Visual: Make AI look where it's going
        self.head.look_at(self.head.position + self.direction)
        self.update_appearance()

    def grow(self):
        new_segment = Entity(model='cube', color=AI_COLOR, scale=1, position=self.body[-1].position)
        self.body.append(new_segment)
        self.update_appearance()
    
    def reset(self):
        for segment in self.body:
            destroy(segment)