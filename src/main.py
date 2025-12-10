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
from ui import GameOverUI, MainMenu, GameHUD
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
current_cam_mode = 'follow'
current_is_aggressive = False

# UI States
main_menu = None
game_over_ui = None
game_hud = None

# Game UI Elements
score = 0
# score_text and game_over_text removed in favor of GameHUD and GameOverUI

# --- GAME LOGIC ---

def get_occupied_positions():
    positions = []
    if snake:
        positions.extend([s.position for s in snake.body])
    if ai_snake:
        positions.extend([s.position for s in ai_snake.body])
    return positions

def start_game(mode, player_name="Guest", cam_mode='follow', is_aggressive=False):
    global snake, ai_snake, food, camera_controller, direction_hints, current_mode, grid, main_menu, current_player_name, game_hud, current_cam_mode, current_is_aggressive
    
    main_menu.enabled = False
    current_mode = mode
    current_player_name = player_name
    current_cam_mode = cam_mode
    current_is_aggressive = is_aggressive
    
    if not grid: grid = WorldGrid()
    
    snake = Snake()
    # direction_hints = DirectionHints(snake)
    
    if cam_mode in ['orbital', 'topdown']:                                                                                                             
       snake.set_strategy('standard')                                                                                                                 
    else:                                                                                                                                                                                                                                                                           
        snake.set_strategy('free_roam')

    if current_mode == 'ai':
        ai_snake = AISnake(start_pos=(3, 0, 3), aggressive_mode=is_aggressive)
    else:
        ai_snake = None 

    food = Food(occupied_positions=get_occupied_positions())
    camera_controller = SnakeCamera(snake)
    camera_controller.set_mode(cam_mode)
    
    # Initialize HUD
    if game_hud: destroy(game_hud)
    game_hud = GameHUD(player_name, current_mode)
    
    update_score(0)

def update_score(new_val):
    global score
    score = new_val
    if game_hud:
        game_hud.update_score(score)

def stop_game():
    global snake, ai_snake, food, direction_hints, camera_controller, game_over_ui, game_hud
    
    if snake:
        for segment in snake.body: destroy(segment)
        # destroy(snake.head_marker)
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

    if game_over_ui:
        destroy(game_over_ui)
        game_over_ui = None

    if game_hud:
        destroy(game_hud)
        game_hud = None

def restart_game():
    stop_game()
    start_game(current_mode, current_player_name, current_cam_mode, current_is_aggressive)

def show_menu():
    stop_game()
    main_menu.update_leaderboard() # Refresh leaderboard in case we added a score
    main_menu.enabled = True

def check_highscore_and_end(message):
    global game_over_ui
    # Save score immediately using the current player name
    leaderboard.save_new_score(current_player_name, score, current_mode)
    
    # Instantiate GameOverUI
    game_over_ui = GameOverUI(
        player_name=current_player_name,
        score=score,
        current_mode=current_mode,
        restart_callback=restart_game,
        menu_callback=show_menu
    )
    
    # 2. Stop movement
    if snake: snake.direction = Vec3(0,0,0)
    if ai_snake: ai_snake.alive = False

def update():
    if not snake: return # Menu mode

    # if camera_controller and snake:
    #     print(f"Camera: {camera_controller.current_mode_name} | Input: {type(snake.current_strategy).__name__}")

    # --- AI Logic ---
    if ai_snake and ai_snake.alive and snake.direction.length() > 0:
        ai_snake.decide_move(food, snake)
        if ai_snake.head.position == food.position:
            ai_snake.grow()
            food.reposition(occupied_positions=get_occupied_positions())
        
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
                food.reposition(occupied_positions=get_occupied_positions())
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