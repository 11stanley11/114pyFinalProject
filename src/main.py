"""
Main entry point of the game.
With DEBUG INPUT enabled.
"""

from ursina import *
from pathlib import Path
import time
import random

# Game Imports
from player import Snake
from food import Food
from world import WorldGrid
from camera import SnakeCamera
from ai import AISnake
import leaderboard
import config
from config import BACKGROUND_COLOR, FULLSCREEN, SNAKE_SPEED, OBSTACLE_COLOR, GRID_SIZE
from ui import GameOverUI, MainMenu, GameHUD

# --- Asset Path Setup ---
# Set asset folder to the project root (parent of 'src')
# This allows loading assets like model='snkb' or texture='pict_for_snkg' directly
# MUST BE SET BEFORE Ursina() INIT if possible, or immediately after import if `application` is available.
# Actually, Ursina() uses it during __init__.
application.asset_folder = Path(__file__).parent.parent
application.development_mode = False # Disable auto-compression of models to prevent 'models_compressed' folder creation

# Fail-safe: Force delete 'models_compressed' if it exists in src to prevent startup crashes
bad_cache = Path(__file__).parent / 'models_compressed'
if bad_cache.exists():
    import shutil
    try:
        shutil.rmtree(bad_cache)
        print("Cleaned up corrupted cache folder.")
    except Exception as e:
        print(f"Warning: Could not clean cache: {e}")

# --- Setup Window ---
app = Ursina(fullscreen=FULLSCREEN)

window.size = (1920, 1080)
window.color = BACKGROUND_COLOR
window.title = "3D Snake - Group Project (DEBUG MODE)"
window.borderless = False 
window.exit_button.visible = False
window.fps_counter.enabled = False
window.vsync = False

# Background
background = Entity(
    parent=camera,
    model='quad',
    texture='pict_for_snkg', 
    scale=(160, 90),
    z=75,
    color=color.white
)

# --- Global Variables ---
grid = WorldGrid()
grid.enabled = False

snake = None
ai_snake = None
food = None
obstacles = []
camera_controller = None
current_mode = None 
current_player_name = "Guest"
current_cam_mode = 'follow'
current_is_aggressive = False

# Game State
game_unpause_time = 0.0
score = 0

# UI States
main_menu = None
game_over_ui = None
game_hud = None

# Audio
bg_music = Audio('bgm.wav', loop=True, autoplay=False, volume=0.5, eternal=True)
eat_sound = Audio('eat apple.wav', loop=False, autoplay=False)
crash_sound = Audio('game-over-arcade-6435.wav', loop=False, autoplay=False)
click_sound = Audio('button.wav', loop=False, autoplay=False)
# Audio Engine "Keep Alive" Workaround
# Fixes issue where music stops if no other sound plays for a while.
keep_alive_sound = Audio('button.wav', loop=False, autoplay=False, volume=0.0) 
last_keep_alive_time = 0.0

# --- GAME LOGIC ---

def get_occupied_positions():
    positions = []
    if snake:
        positions.extend([s.position for s in snake.body])
    if ai_snake:
        positions.extend([s.position for s in ai_snake.body])
    positions.extend([obs.position for obs in obstacles])
    return positions

def start_game(mode, player_name="Guest", cam_mode='follow', is_aggressive=False, preview=False, grid_size=None):
    global snake, ai_snake, food, camera_controller, current_mode, grid, game_hud, current_cam_mode, current_is_aggressive, game_unpause_time, current_player_name
    
    if snake or ai_snake or food:
        stop_game()
        
    game_unpause_time = 0.0
    if not preview:
        main_menu.enabled = False
    
    current_mode = mode
    current_player_name = player_name
    current_cam_mode = cam_mode
    current_is_aggressive = is_aggressive
    
    # Handle Grid Size
    if grid_size is not None:
        config.GRID_SIZE = grid_size

    # Audio Logic
    if not preview and not bg_music.playing:
        bg_music.play()
    elif preview and bg_music.playing:
        bg_music.stop()
    
    # Grid
    if grid:
        grid.set_size(config.GRID_SIZE)
        grid.enabled = True
    
    # Reset Logic
    if snake: snake.destroy_entities()
    snake = None
    if ai_snake: 
        ai_snake.reset()
        ai_snake = None
    if food: 
        destroy(food)
        food = None
    
    for obs in obstacles: destroy(obs)
    obstacles.clear()

    if camera_controller: 
        destroy(camera_controller)
        camera_controller = None
    if game_hud and not preview: 
        destroy(game_hud)
        game_hud = None

    # Spawn Entities
    snake = Snake()
    
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
    if not preview:
        game_hud = GameHUD(player_name, current_mode)
        update_score(0)

def update_score(new_val):
    global score
    score = new_val
    if game_hud:
        game_hud.update_score(score)

def stop_game():
    global snake, ai_snake, food, camera_controller, game_over_ui, game_hud
    
    if snake:
        for segment in snake.body: destroy(segment)
        snake.destroy_entities()
        snake = None
        
    if ai_snake:
        ai_snake.reset()
        ai_snake = None
        
    if food:
        destroy(food)
        food = None

    for obs in obstacles: destroy(obs)
    obstacles.clear()
        
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
    bg_music.stop()
    main_menu.update_leaderboard()
    main_menu.enabled = True
    main_menu.update_mode_display()

def check_highscore_and_end(message):
    global game_over_ui
    leaderboard.save_new_score(current_player_name, score, current_mode)
    
    game_over_ui = GameOverUI(
        player_name=current_player_name,
        score=score,
        current_mode=current_mode,
        restart_callback=restart_game,
        menu_callback=show_menu
    )
    crash_sound.play()
    bg_music.stop()
    
    if snake: 
        snake.direction = Vec3(0,0,0)
        snake.destroy_entities() 
    if ai_snake: 
        ai_snake.alive = False

def spawn_obstacle():
    occupied = get_occupied_positions()
    if food: occupied.append(food.position)
    
    half_grid = config.GRID_SIZE // 2
    valid_pos = None
    
    for _ in range(100):
        pos_tuple = (
            random.randint(-half_grid + 1, half_grid - 1),
            random.randint(-half_grid + 1, half_grid - 1),
            random.randint(-half_grid + 1, half_grid - 1)
        )
        is_occupied = False
        for occ in occupied:
            if round(occ.x) == pos_tuple[0] and round(occ.y) == pos_tuple[1] and round(occ.z) == pos_tuple[2]:
                is_occupied = True
                break
        if not is_occupied:
            valid_pos = pos_tuple
            break
            
    if valid_pos:
        obs = Entity(model='cube', color=OBSTACLE_COLOR, scale=1, position=valid_pos)
        obstacles.append(obs)

def update():
    global game_unpause_time, last_keep_alive_time
    
    if main_menu and main_menu.enabled: return

    # Ensure background music is playing if the game is active (and not Game Over)
    # This fixes an issue where music might stop unexpectedly.
    if snake and not game_over_ui and not bg_music.playing:
        bg_music.play()

    # AUDIO WORKAROUND: Play a silent sound every 1.5s to keep the audio engine "awake"
    # This prevents the background music from pausing due to driver timeouts/sleeping.
    if snake and not game_over_ui and time.time() - last_keep_alive_time > 1.5:
        keep_alive_sound.play()
        last_keep_alive_time = time.time()

    if time.time() < game_unpause_time: return
    if not snake: return 

    if ai_snake and ai_snake.alive and snake.direction.length() > 0:
        ai_snake.decide_move(food, snake)
        if ai_snake.head.position == food.position:
            ai_snake.grow()
            food.reposition(occupied_positions=get_occupied_positions())
        for segment in snake.body:
            if ai_snake.head.position == segment.position:
                check_highscore_and_end("The AI ate you!")
                return

    if snake.direction.length() > 0:
        if time.time() - snake.last_move_time > 1 / SNAKE_SPEED:
            snake.last_move_time = time.time()
            snake.handle_turn()

            if snake.will_collide(config.GRID_SIZE):
                check_highscore_and_end("You crashed!")
                return
            
            if ai_snake:
                next_pos = snake.head.position + snake.direction.normalized()
                for segment in ai_snake.body:
                    if next_pos == segment.position:
                        check_highscore_and_end("You hit the AI!")
                        return

            snake.move()
            
            if current_mode == 'obstacles':
                for obs in obstacles:
                    if snake.head.position == obs.position:
                        check_highscore_and_end("You crashed into an obstacle!")
                        return

            if snake.head.position == food.position:
                if current_mode == 'reverse':
                    snake.reverse_and_grow()
                    game_unpause_time = time.time() + 0.75
                elif current_mode == 'obstacles':
                    snake.grow()
                    spawn_obstacle()
                else:
                    snake.grow()
                
                food.reposition(occupied_positions=get_occupied_positions())
                update_score(score + 1)
                eat_sound.play()

def input(key):
    # Mouse interaction
    if key == 'left mouse down':
        if mouse.hovered_entity and isinstance(mouse.hovered_entity, Button):
            click_sound.play()

    if key == 'escape': application.quit()

    # Gamepad Mapping
    mapped_key = None
    if key == 'gamepad dpad up': mapped_key = 'w'
    elif key == 'gamepad dpad down': mapped_key = 's'
    elif key == 'gamepad dpad left': mapped_key = 'a'
    elif key == 'gamepad dpad right': mapped_key = 'd'
    elif key == 'gamepad y': mapped_key = 'r' 

    key = mapped_key if mapped_key else key

    # --- MOVEMENT INPUT (DEBUG ENABLED) ---
    if snake and snake.direction.length() > 0:
        if key in ['w', 'a', 's', 'd', 'q', 'e', 'space', 'shift']:
            # 1. Print input key
            print(f"\n>>> [USER INPUT] Key Pressed: {key}")
            # 2. Print state BEFORE strategy handles it
            snake.print_debug_state(tag="BEFORE STRATEGY")
            
            snake.turn(key)
            
            # (Optional) Print immediately, though handle_turn happens in update()
            # This helps confirms the queue is receiving data
            print(f"    (Action Queued. Queue len: {len(snake.turn_buffer)})")

    
    # RESTART/MENU LOGIC:
    if snake and snake.direction.length() == 0: 
        if key == 'r': restart_game()
        if key == 'm' or key =='gamepad start': show_menu()

def on_menu_mode_changed(mode, cam_mode, is_aggressive, grid_size):
    start_game(mode, "Guest", cam_mode, is_aggressive, preview=True, grid_size=grid_size)

# --- STARTUP ---
main_menu = MainMenu(start_game, application.quit, bg_music, grid, on_menu_mode_changed)

# Initialize preview
start_game('classic', "Guest", 'follow', False, preview=True, grid_size=8)
main_menu.enabled = True 

if __name__ == '__main__':
    app.run()
