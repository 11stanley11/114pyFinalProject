"""
Main entry point of the game.
"""

from ursina import *
from player import Snake
from food import Food
from world import WorldGrid
from camera import SnakeCamera
from ui import DirectionHints
from ai import AISnake
import leaderboard
from config import GRID_SIZE, BACKGROUND_COLOR, FULLSCREEN, SNAKE_SPEED
import time

# --- Global Game State ---
# 遊戲模式: 'player' (預設), 或 'ai' (啟用 AI 玩家)
current_mode = 'player' 
ai_snake = None # AI Snake instance

# --- Setup Window ---
app = Ursina(fullscreen=FULLSCREEN)
grid = WorldGrid()
score = 0
score_text = Text(text=f"Score: {score}", position=(-0.85, 0.45), scale=2)
game_over_text = Text(text="", origin=(0, 0), scale=3)

# 初始化變數
snake = None
food = None
camera_controller = None

# --- Game Window ---
window.color = BACKGROUND_COLOR

def check_highscore_and_end(message):
    """Checks for high score and displays game over message."""
    global snake, game_over_text
    
    # 計算分數
    final_score = len(snake.body) - 3
    
    game_over_text.text = f"GAME OVER! {message}\nScore: {final_score}\nPress R to Restart"
    game_over_text.enabled = True
    score_text.enabled = False
    
    # 停止蛇的移動
    snake.direction = Vec3(0, 0, 0)
    
def initialize_game():
    """Initializes the game for the first run."""
    global snake, food, camera_controller, ai_snake
    
    # 創建玩家蛇
    snake = Snake()
    # 創建食物
    food = Food()
    # 創建鏡頭控制器
    camera_controller = SnakeCamera(snake)
    # 創建方向提示 UI
    DirectionHints(snake)

    # 根據模式創建 AI 蛇
    if current_mode == 'ai':
        # 假設 AI 從不同的起始位置開始，以避免與玩家蛇碰撞
        ai_snake = AISnake(start_pos=(3, 0, 3)) 
    else:
        ai_snake = None
    
    update_score(0)
    score_text.enabled = True
    game_over_text.enabled = False


def restart_game():
    """
    Resets the game to its initial state.
    """
    global snake, food, score, score_text, game_over_text, camera_controller, ai_snake

    # 銷毀舊的實體
    if snake:
        for segment in snake.body:
            destroy(segment)
        destroy(snake.head_marker)
    if food:
        destroy(food)
    if ai_snake:
        for segment in ai_snake.body:
            destroy(segment)
        destroy(ai_snake.head_marker)

    # 重新初始化遊戲
    initialize_game()


def update_score(new_val):
    global score
    score = new_val
    score_text.text = f"Score: {score}"
    game_over_text.text = ""

    # 更新鏡頭以追蹤新的蛇
    if camera_controller:
        camera_controller.snake = snake

def update():
    """
    This function is called every frame by Ursina.
    Handles player and AI snake movement, collisions, and scoring.
    """
    global score
    
    # 檢查是否達到移動時間間隔
    if time.time() - snake.last_move_time > 1 / SNAKE_SPEED:
        snake.last_move_time = time.time()
        
        # --- 1. 玩家蛇處理 ---
        if snake.direction.length() > 0: # 如果遊戲活躍
            snake.handle_turn()
            
            # 碰撞檢測 (牆壁/自身)
            if snake.will_collide(GRID_SIZE):
                check_highscore_and_end("You crashed!")
                return
            
            # 碰撞檢測 (與 AI 蛇)
            if ai_snake:
                next_pos = snake.head.position + snake.direction.normalized()
                for segment in ai_snake.body:
                    if next_pos == segment.position:
                        check_highscore_and_end("You hit the AI!")
                        return

            # 執行移動
            snake.move()

            # 食物檢查
            if snake.head.position == food.position:
                snake.grow()
                food.reposition()
                update_score(score + 1)

        # --- 2. AI 蛇處理 ---
        if ai_snake and ai_snake.direction.length() > 0:
            # AI 決策轉向 (需要 ai.py 中的 AISnake.handle_turn(food_position) 實現)
            # 注意: 這裡假設 AISnake 的 handle_turn 方法接受食物位置
            ai_snake.handle_turn(food.position) 

            # AI 碰撞檢測 (AI 自身碰撞或牆壁碰撞)
            # 在多人模式中，AI 應避免碰撞或死亡，但為了不干擾遊戲，我們通常只處理 AI 吃到食物。
            
            # 執行 AI 移動
            ai_snake.move()

            # AI 食物檢查
            if ai_snake.head.position == food.position:
                ai_snake.grow()
                # 重新生成食物
                food.reposition()


def input(key):
    """
    This function is called by Ursina when a key is pressed.
    """
    global current_mode, ai_snake
    
    # 玩家方向控制
    if key in ['w', 'a', 's', 'd', 'q', 'e']:
        snake.turn(key)

    # 重啟遊戲
    if key == 'r' and snake.direction.length() == 0:
        restart_game()
    
    # P 鍵用於切換模式
    if key == 'p':
        if current_mode == 'player':
            current_mode = 'ai'
            print("Switched to AI Mode (AI snake enabled).")
        else:
            current_mode = 'player'
            print("Switched to Player Mode (AI snake disabled).")
        
        # 切換模式後自動重啟遊戲以應用變更
        restart_game()


def main():
    """
    Initializes and starts the game loop.
    """
    # 初始啟動
    initialize_game() 
    app.run()

if __name__ == '__main__':
    main()