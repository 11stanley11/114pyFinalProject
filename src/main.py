"""
Main entry point of the game.
"""

from ursina import Ursina, window, Text, destroy, Vec3
from player import Snake
from food import Food
from world import WorldGrid
from camera import SnakeCamera
from config import GRID_SIZE, BACKGROUND_COLOR, FULLSCREEN, SNAKE_SPEED
import time

# --- Global Game Objects ---
app = Ursina(fullscreen=FULLSCREEN)
grid = WorldGrid()
snake = Snake()
food = Food()
# 假設 SnakeCamera 已經在 camera.py 中正確定義
camera_controller = SnakeCamera(snake) 
score = 0
score_text = Text(text=f"Score: {score}", position=(-0.85, 0.45), scale=2)
game_over_text = Text(text="", origin=(0, 0), scale=3)

# --- Game Window ---
window.color = BACKGROUND_COLOR
# 確保 Ursina 不會自動啟用 EditorCamera 影響 SnakeCamera 
window.forced_aspect_ratio = 1.77 # 設置一個常見的螢幕比例，提升視覺效果

def restart_game():
    """
    Resets the game to its initial state.
    """
    global snake, food, score, score_text, game_over_text, camera_controller

    # Destroy old entities
    for segment in snake.body:
        destroy(segment)
    destroy(snake.head_marker)
    destroy(food)

    # Create new entities
    snake = Snake()
    food = Food()

    # Reset score and text
    score = 0
    score_text.text = f"Score: {score}"
    game_over_text.text = ""

    # Update the camera to follow the new snake
    camera_controller.snake = snake
    # 重新對齊鏡頭
    if hasattr(camera_controller, '_snap_to_target'):
        camera_controller._snap_to_target()

def update():
    """
    This function is called every frame by Ursina.
    """
    global score
    
    # 在每一幀更新相機的位置和視角
    # 確保攝影機平滑地跟隨蛇頭
    camera_controller.update() 
    
    if snake.direction.length() > 0: # If game is active
        if time.time() - snake.last_move_time > 1 / SNAKE_SPEED:
            snake.last_move_time = time.time()

            snake.handle_turn()

            # Check for game over
            if snake.will_collide(GRID_SIZE):
                game_over_text.text = "Game Over\n(Press 'r' to restart)"
                game_over_text.color = window.color.invert()
                snake.direction = Vec3(0, 0, 0)  # Stop the snake
                return # Skip the rest of the update
            
            snake.move()

            # Check for collision with food
            if snake.head.position == food.position:
                snake.grow()
                food.reposition()
                score += 1
                score_text.text = f"Score: {score}"

def input(key):
    """
    This function is called by Ursina when a key is pressed.
    """
    if key in ['w', 'a', 's', 'd']: # Removed 'q' and 'e' for roll
        snake.turn(key)
    if key == 'r' and snake.direction.length() == 0:
        restart_game()
        
    # 新增：可以讓使用者按下 Esc 鍵退出遊戲
    if key == 'escape':
        quit()


def main():
    """
    This function is now only responsible for starting the game.
    """
    app.run()

if __name__ == '__main__':
    main()