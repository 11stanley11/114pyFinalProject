'''
"Main entry point of the game."
'''

from ursina import *
from player import Snake
from food import Food
from world import WorldGrid
from camera import SnakeCamera
# from ui import DirectionHints
from ai import AISnake
import leaderboard
from config import GRID_SIZE, BACKGROUND_COLOR, FULLSCREEN, SNAKE_SPEED
from ui import GameOverUI, MainMenu
import time

# --- Setup Window ---
app = Ursina(fullscreen=FULLSCREEN)
window.color = BACKGROUND_COLOR
window.title = "3D Snake - Group Project"
window.borderless = False 

# --- Global Variables ---
grid = None
snake = None
ai_snake = None
food = None
camera_controller = None
direction_hints = None
current_mode = None 
current_player_name = "Guest"

# UI States
main_menu = None

# Game UI Elements
score = 0
score_text = Text(text="", position=(-0.85, 0.45), scale=2, enabled=False)
game_over_text = Text(text="", origin=(0, 0), scale=3, enabled=False)

# --- GAME LOGIC ---

def start_game(mode, player_name="Guest"):
    global snake, ai_snake, food, camera_controller, direction_hints, current_mode, grid, main_menu, current_player_name
    
    main_menu.enabled = False
    current_mode = mode
    current_player_name = player_name
    
    if not grid: grid = WorldGrid()
    
    snake = Snake()
    # direction_hints = DirectionHints(snake)
    
    if current_mode == 'ai':
        ai_snake = AISnake(start_pos=(3, 0, 3))
    else:
        ai_snake = None 

    food = Food()
    camera_controller = SnakeCamera(snake)
    
    update_score(0)
    score_text.enabled = True
    game_over_text.enabled = False

def update_score(new_val):
    global score
    score = new_val
    score_text.text = f"Score: {score}"

def stop_game():
    global snake, ai_snake, food, direction_hints, camera_controller
    
    if snake:
        for segment in snake.body: destroy(segment)
        destroy(snake.head_marker)
        snake = None
        
    if ai_snake:
        ai_snake.reset()
        ai_snake = None
        
    if food:
        destroy(food)
        food = None
        
    if direction_hints:
        for hint in direction_hints.hints: destroy(hint)
        destroy(direction_hints)
        direction_hints = None

    if camera_controller:
        destroy(camera_controller)
        camera_controller = None

    score_text.enabled = False
    game_over_text.enabled = False

def restart_game():
    stop_game()
    start_game(current_mode, current_player_name)

def show_menu():
    stop_game()
    main_menu.update_leaderboard() # Refresh leaderboard in case we added a score
    main_menu.enabled = True

def check_highscore_and_end(message):
    # Save score immediately using the current player name
    leaderboard.save_new_score(current_player_name, score, current_mode)
    
    # 1. Show Game Over text with score
    game_over_text.text = f"{message}\nFinal Score: {score}\n(Press 'r' to restart)\n(Press 'm' for Menu)"
    game_over_text.color = window.color.invert()
    game_over_text.enabled = True
    
    # 2. Stop movement
    if snake: snake.direction = Vec3(0,0,0)
    if ai_snake: ai_snake.alive = False

def update():
    if not snake: return # Menu mode

    # --- AI Logic ---
    if ai_snake and ai_snake.alive and snake.direction.length() > 0:
        ai_snake.decide_move(food, snake)
        if ai_snake.head.position == food.position:
            ai_snake.grow()
            food.reposition()
        
        # AI eats Player
        for segment in snake.body:
            if ai_snake.head.position == segment.position:
                check_highscore_and_end("The AI ate you!")
                return

    # --- Player Logic ---
    if snake.direction.length() > 0:
        if time.time() - snake.last_move_time > 1 / SNAKE_SPEED:
            snake.last_move_time = time.time()
            snake.handle_turn()

            if snake.will_collide(GRID_SIZE):
                check_highscore_and_end("You crashed!")
                return
            
            if ai_snake:
                next_pos = snake.head.position + snake.direction.normalized()
                for segment in ai_snake.body:
                    if next_pos == segment.position:
                        check_highscore_and_end("You hit the AI!")
                        return

            snake.move()

            if snake.head.position == food.position:
                snake.grow()
                food.reposition()
                update_score(score + 1)

def input(key):
    if key == 'escape': application.quit()

    if snake and snake.direction.length() > 0:
        if key in ['w', 'a', 's', 'd', 'q', 'e', 'space', 'shift']:
            snake.turn(key)
    
    # RESTART/MENU LOGIC:
    if snake and snake.direction.length() == 0: 
        if key == 'r': restart_game()
        if key == 'm': show_menu()

# --- STARTUP ---
main_menu = MainMenu(start_game, application.quit)

if __name__ == '__main__':
    app.run()
