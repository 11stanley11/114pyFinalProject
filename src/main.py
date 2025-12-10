"""
Main entry point of the game.
Fixed: Input processing is no longer blocked if snake stops moving.
"""
from ursina import application
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

# UI States
main_menu = None
leaderboard_ui = None
highscore_input = None 

# Game UI Elements
score = 0
score_text = Text(text="", position=(-0.85, 0.45), scale=2, enabled=False)
game_over_text = Text(text="", origin=(0, 0), scale=3, enabled=False)

# --- UI CLASSES ---
class MainMenu(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.bg = Entity(parent=self, model='quad', scale=(20, 10), color=color.black66, z=10)
        self.title = Text(text='3D SNAKE', parent=self, scale=4, y=0.35, origin=(0,0), color=color.green, z=-1)
        self.btn_classic = Button(text='Classic Mode (Solo)', color=color.azure, scale=(0.45, 0.08), position=(0, 0.1), parent=self, z=-1)
        self.btn_classic.on_click = lambda: start_game('classic')
        self.btn_ai = Button(text='Survival Mode (vs AI)', color=color.orange, scale=(0.45, 0.08), position=(0, -0.05), parent=self, z=-1)
        self.btn_ai.on_click = lambda: start_game('ai')
        self.btn_leaderboard = Button(text='Leaderboard', color=color.gold, scale=(0.4, 0.08), position=(0, -0.2), parent=self, z=-1)
        self.btn_leaderboard.on_click = show_leaderboard
        self.btn_quit = Button(text='Quit', color=color.red, scale=(0.3, 0.06), position=(0, -0.35), parent=self, z=-1)
        self.btn_quit.on_click = application.quit

class LeaderboardUI(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui, enabled=False)
        self.bg = Entity(parent=self, model='quad', scale=(20, 10), color=color.black90, z=9)
        self.title = Text(text='TOP SCORES', parent=self, scale=3, y=0.4, origin=(0,0), color=color.gold, z=-1)
        self.score_lines = Text(text='', parent=self, scale=1.5, position=(0, 0.25), origin=(0,1), z=-1)
        self.btn_back = Button(text='Back', color=color.gray, scale=(0.2, 0.08), position=(0, -0.4), parent=self, z=-1)
        self.btn_back.on_click = show_menu

    def refresh(self):
        scores = leaderboard.load_scores()
        text_content = ""
        for i, entry in enumerate(scores):
            name = entry['name'][:10].ljust(10)
            text_content += f"{i+1}. {name} - {entry['score']}\n"
        self.score_lines.text = text_content

class HighScoreInput(Entity):
    def __init__(self, final_score):
        super().__init__(parent=camera.ui)
        self.final_score = final_score
        self.bg = Entity(parent=self, model='quad', scale=(10, 5), color=color.black90, z=8)
        self.title = Text(text='NEW HIGH SCORE!', parent=self, scale=2.5, y=0.2, origin=(0,0), color=color.gold, z=-1)
        self.sub = Text(text=f'You scored: {final_score}', parent=self, scale=1.5, y=0.1, origin=(0,0), z=-1)
        self.inp = InputField(parent=self, y=-0.1, limit_content_to='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', active=True, scale=1.5)
        self.inp.text_color = color.white
        self.inp.max_lines = 1
        self.btn_submit = Button(text='Save', color=color.green, scale=(0.2, 0.08), position=(0, -0.25), parent=self, z=-1)
        self.btn_submit.on_click = self.submit_score

    def submit_score(self):
        global highscore_input
        name = self.inp.text.strip()
        if not name: name = "Anonymous"
        leaderboard.save_new_score(name, self.final_score)
        destroy(self)
        highscore_input = None
        show_leaderboard()

# --- GAME LOGIC ---

def start_game(mode):
    global snake, ai_snake, food, camera_controller, direction_hints, current_mode, grid, main_menu, leaderboard_ui
    main_menu.enabled = False
    leaderboard_ui.enabled = False
    current_mode = mode
    if not grid: grid = WorldGrid()
    snake = Snake()
    camera_controller = SnakeCamera(snake) 
    direction_hints = DirectionHints(snake)
    if current_mode == 'ai':
        ai_snake = AISnake(start_pos=(3, 0, 3))
    else:
        ai_snake = None 
    food = Food()
    update_score(0)
    score_text.enabled = True
    game_over_text.enabled = False

def update_score(new_val):
    global score
    score = new_val
    score_text.text = f"Score: {score}"

def stop_game():
    global snake, ai_snake, food, direction_hints, camera_controller, highscore_input
    if snake:
        for segment in snake.body: destroy(segment)
        destroy(snake.head_marker)
        snake = None
    if ai_snake: ai_snake.reset()
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
    if highscore_input:
        destroy(highscore_input)
        highscore_input = None
    score_text.enabled = False
    game_over_text.enabled = False

def restart_game():
    stop_game()
    start_game(current_mode)

def show_menu():
    stop_game()
    leaderboard_ui.enabled = False
    main_menu.enabled = True

def show_leaderboard():
    stop_game()
    main_menu.enabled = False
    leaderboard_ui.enabled = True
    leaderboard_ui.refresh()

def check_highscore_and_end(message):
    global highscore_input
    game_over_text.text = f"{message}\nFinal Score: {score}"
    game_over_text.color = window.color.invert()
    game_over_text.enabled = True
    if ai_snake: ai_snake.alive = False
    if leaderboard.is_high_score(score):
        invoke(lambda: trigger_highscore_input(), delay=1.5)
    else:
        game_over_text.text += "\n\n(Press 'Y' to restart)\n(Press 'X' for Menu)"

def trigger_highscore_input():
    global highscore_input
    game_over_text.enabled = False 
    highscore_input = HighScoreInput(score)

def update():
    if not snake: return # Menu mode

    if game_over_text.enabled or highscore_input:
        return

    # --- AI Logic ---
    if ai_snake and ai_snake.alive:
        ai_snake.decide_move(food, snake) 
        if ai_snake.will_collide_self(GRID_SIZE):
            ai_snake.alive = False
            check_highscore_and_end("The AI crashed into itself!")
            return 
        if ai_snake.head.position == food.position:
            ai_snake.grow()
            food.reposition()
        for segment in snake.body:
            if ai_snake.head.position == segment.position:
                check_highscore_and_end("The AI ate you!")
                return

    # --- Player Logic ---
    # 速度控制
    if time.time() - snake.last_move_time > 1 / SNAKE_SPEED:
        snake.last_move_time = time.time()
        
        snake.handle_turn()

        if snake.direction.length() > 0.001:
            next_pos = snake.head.position + snake.direction.normalized()
            
            if snake.will_collide(GRID_SIZE):
                check_highscore_and_end("You crashed!")
                return
            
            if ai_snake:
                for segment in ai_snake.body:
                    if next_pos == segment.position:
                        check_highscore_and_end("You hit the AI!")
                        return

            snake.move()

            if snake.head.position == food.position:
                snake.grow()
                food.reposition()
                update_score(score + 1)
        else:
            # 如果速度為0，嘗試重置為預設方向 (避免永遠卡住)
            # snake.direction = Vec3(0,1,0)
            pass 

def input(key):
    global highscore_input
    if key == 'escape': application.quit()

    mapped_key = None
    if key == 'gamepad dpad up': mapped_key = 'w'
    elif key == 'gamepad dpad down': mapped_key = 's'
    elif key == 'gamepad dpad left': mapped_key = 'a'
    elif key == 'gamepad dpad right': mapped_key = 'd'
    elif key == 'gamepad a': mapped_key = '1'  
    elif key == 'gamepad b': mapped_key = '2' 
    elif key == 'gamepad x': mapped_key = 'm' 

    final_key = mapped_key if mapped_key else key

    if snake and not game_over_text.enabled:
        valid_keys = ['w', 'a', 's', 'd', 'q', 'e', '1', '2']
        if final_key in valid_keys:
            snake.turn(final_key)
            
        if key == 'gamepad right shoulder' or key == 'gamepad left shoulder' or key == 'c':
            if "Free Roam" in snake.current_strategy.get_name():
                snake.turn('1') 
            else:
                snake.turn('2') 
    
    if game_over_text.enabled and not highscore_input: 
        if final_key == 'r' or key == 'gamepad y': restart_game()
        if final_key == 'm': show_menu()

# --- STARTUP ---
main_menu = MainMenu()
leaderboard_ui = LeaderboardUI()

if __name__ == '__main__':
    app.run()