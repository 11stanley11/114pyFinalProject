# Contains the AI class for computer-controlled snakes.
from ursina import Entity, Vec3, color, distance, destroy
import random
import time
from config import AI_COLOR, GRID_SIZE, AI_SPEED

class AISnake:
    def __init__(self, start_pos=(5, 0, 5)):
        self.body = [
            Entity(model='cube', color=AI_COLOR, scale=1, position=start_pos),
            Entity(model='cube', color=AI_COLOR, scale=1, position=(start_pos[0], start_pos[1]-1, start_pos[2]))
        ]
        self.head = self.body[0]
        self.direction = Vec3(0, 1, 0)
        self.last_move_time = time.time()
        self.speed = AI_SPEED
        self.alive = True

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

        # Simple AI: Pick the move that minimizes distance to food
        best_move = safe_moves[0]
        min_dist = float('inf')

        # Shuffle safe moves so if distances are equal, it picks randomly 
        # (prevents getting stuck in loops)
        random.shuffle(safe_moves) 

        for move in safe_moves:
            next_pos = self.head.position + move
            dist_to_food = distance(next_pos, food.position)
            
            if dist_to_food < min_dist:
                min_dist = dist_to_food
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

    def grow(self):
        new_segment = Entity(model='cube', color=AI_COLOR, scale=1, position=self.body[-1].position)
        self.body.append(new_segment)
    
    def reset(self):
        for segment in self.body:
            destroy(segment)
    def will_collide_self(self, grid_size):
        """
        檢查 AI 蛇是否會在下一步撞到自己。
        """
        # 計算 AI 蛇的下一步位置
        next_head_position = self.head.position + self.direction.normalized()

        # 檢查自身碰撞 (從第二段身體開始檢查)
        for segment in self.body[1:]:
            if next_head_position == segment.position:
                return True
        return False