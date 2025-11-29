"""
Main entry point of the game.
"""

from ursina import Ursina, window, Text, destroy, Vec3
from player import Snake
from food import Food
from world import WorldGrid
from camera import SnakeCamera
from config import GRID_SIZE, BACKGROUND_COLOR, FULLSCREEN, SNAKE_SPEED
from ui import GameOverUI
import time

# --- Global Game Objects ---
app = Ursina(fullscreen=FULLSCREEN)
grid = WorldGrid()
snake = Snake()
food = Food()
camera_controller = SnakeCamera(snake)
score = 0
score_text = Text(text=f"Score: {score}", position=(-0.85, 0.45), scale=2)
game_over_ui = None


# --- Game Window ---
window.color = BACKGROUND_COLOR

def restart_game():
    """
    Resets the game to its initial state.
    """
    global snake, food, score, score_text, camera_controller, game_over_ui

    # Destroy old entities
    for segment in snake.body:
        destroy(segment)
    destroy(snake.head_marker)
    destroy(food)
    if game_over_ui:
        game_over_ui.close()
        game_over_ui = None

    # Create new entities
    snake = Snake()
    food = Food()

    # Reset score and text
    score = 0
    score_text.text = f"Score: {score}"

    # Update the camera to follow the new snake
    camera_controller.snake = snake

def update():
    """
    This function is called every frame by Ursina.
    """
    global score, game_over_ui
    
    if snake.direction.length() > 0: # If game is active
        if time.time() - snake.last_move_time > 1 / SNAKE_SPEED:
            snake.last_move_time = time.time()

            snake.handle_turn()

            # Check for game over
            if snake.will_collide(GRID_SIZE):
                snake.direction = Vec3(0, 0, 0)  # Stop the snake
                if not game_over_ui:
                    game_over_ui = GameOverUI(current_score=score, restart_func=restart_game)
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
    if key in ['w', 'a', 's', 'd', 'q', 'e']:
        snake.turn(key)
    if key == 'r' and snake.direction.length() == 0:
        restart_game()


def main():
    """
    This function is now only responsible for starting the game.
    """
    app.run()

if __name__ == '__main__':
    main()
