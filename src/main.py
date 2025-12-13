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
import config
from config import BACKGROUND_COLOR, FULLSCREEN, SNAKE_SPEED, OBSTACLE_COLOR
from ui import GameOverUI, MainMenu, GameHUD
import time
import random # Needed for obstacle spawning

# --- Setup Window ---
app = Ursina(fullscreen=FULLSCREEN)
window.color = BACKGROUND_COLOR
window.title = "3D Snake - Group Project"
window.borderless = False 
window.exit_button.visible = False
window.fps_counter.enabled = False
window.entity_counter.enabled = False
window.collider_counter.enabled = False
window.vsync = False

# --- Global Variables ---
grid = WorldGrid() # Pre-load grid to avoid lag during gameplay start
grid.enabled = False

snake = None
ai_snake = None
food = None
obstacles = [] # List to store obstacle entities
camera_controller = None
direction_hints = None
current_mode = None 
current_player_name = "Guest"
current_cam_mode = 'follow'
current_is_aggressive = False

# Global game state for pausing
game_unpause_time = 0.0

# UI States
main_menu = None
game_over_ui = None
game_hud = None

# Game UI Elements
score = 0
# score_text and game_over_text removed in favor of GameHUD and GameOverUI

# Background Music 
bg_music = Audio('../assets/bgm.wav', loop=True, autoplay=False, volume=0.5)

# Sound Effects 
eat_sound = Audio('../assets/eat apple.wav', loop=False, autoplay=False)
crash_sound = Audio('../assets/game-over-arcade-6435.wav', loop=False, autoplay=False)
click_sound = Audio('../assets/button.wav', loop=False, autoplay=False)

# --- GAME LOGIC ---

def get_occupied_positions():
    positions = []
    if snake:
        positions.extend([s.position for s in snake.body])
    if ai_snake:
        positions.extend([s.position for s in ai_snake.body])
    # Add obstacles to occupied positions
    positions.extend([obs.position for obs in obstacles])
    return positions

def start_game(mode, player_name="Guest", cam_mode='follow', is_aggressive=False, preview=False, grid_size=None):
    global snake, ai_snake, food, camera_controller, direction_hints, current_mode, grid, main_menu, current_player_name, game_hud, current_cam_mode, current_is_aggressive, game_unpause_time
    
    game_unpause_time = 0.0
    if not preview:
        main_menu.enabled = False
    
    current_mode = mode
    current_player_name = player_name
    current_cam_mode = cam_mode
    current_is_aggressive = is_aggressive
    
    # Handle Grid Size
    target_grid_size = grid_size if grid_size is not None else config.GRID_SIZE
    if grid_size is not None:
        config.GRID_SIZE = grid_size

    # Only play music if this is a real game, not a preview
    if not preview and not bg_music.playing:
        bg_music.play()
    elif preview and bg_music.playing:
        bg_music.stop()
    
    # Update grid size visibility (instant, no rebuild)
    if grid:
        grid.set_size(config.GRID_SIZE)
        grid.enabled = True
    
    # Clean up existing entities if they exist (for preview updates)
    if snake:
        for segment in snake.body: destroy(segment)
        snake = None
    if ai_snake:
        ai_snake.reset()
        ai_snake = None
    if food:
        destroy(food)
        food = None
    
    # Clean up obstacles
    for obs in obstacles:
        destroy(obs)
    obstacles.clear()

    if camera_controller:
        destroy(camera_controller)
        camera_controller = None
    if game_hud and not preview:
        destroy(game_hud)
        game_hud = None

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
    
    # Initialize HUD only if playing
    if not preview:
        if game_hud: destroy(game_hud)
        game_hud = GameHUD(player_name, current_mode)
        update_score(0)
    
    # If preview, we might want to rotate the camera or something, but standard is fine.


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

    # Clean up obstacles
    for obs in obstacles:
        destroy(obs)
    obstacles.clear()
        
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
    bg_music.stop() # Stop music when returning to menu
    
    main_menu.update_leaderboard() # Refresh leaderboard in case we added a score
    main_menu.enabled = True
    
    # Force update preview
    main_menu.update_mode_display()

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
    crash_sound.play()      # <--- Play crash sound
    bg_music.stop()
    # 2. Stop movement
    if snake: snake.direction = Vec3(0,0,0)
    if ai_snake: ai_snake.alive = False

def spawn_obstacle():
    occupied = get_occupied_positions()
    # Also ensure we don't spawn on the CURRENT food position (though it might move soon, better safe)
    if food:
        occupied.append(food.position)
    
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
    global game_unpause_time
    
    # Don't update game logic if menu is open
    if main_menu and main_menu.enabled:
        return

    if time.time() < game_unpause_time:
        return # Pause game logic during reversal animation

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
            
            # Check Obstacle Collision
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
    if key == 'left mouse down':
        # Check if the mouse is hovering over SOMETHING, and if that something is a Button
        if mouse.hovered_entity and isinstance(mouse.hovered_entity, Button):
            click_sound.play()

    if key == 'escape': application.quit()

    if snake and snake.direction.length() > 0:
        if key in ['w', 'a', 's', 'd', 'q', 'e', 'space', 'shift']:
            snake.turn(key)
    
    # RESTART/MENU LOGIC:
    if snake and snake.direction.length() == 0: 
        if key == 'r': restart_game()
        if key == 'm': show_menu()

def on_menu_mode_changed(mode, cam_mode, is_aggressive, grid_size):
    # Update the background preview
    start_game(mode, "Guest", cam_mode, is_aggressive, preview=True, grid_size=grid_size)

# --- STARTUP ---
main_menu = MainMenu(start_game, application.quit, bg_music, grid, on_menu_mode_changed)

# Initialize preview
start_game('classic', "Guest", 'follow', False, preview=True, grid_size=8)
# Re-enable menu because start_game(preview=True) keeps it enabled, but let's be safe
main_menu.enabled = True 

if __name__ == '__main__':
    app.run()
