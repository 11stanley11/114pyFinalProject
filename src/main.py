"""
Main entry point of the game.
"""

from ursina import Ursina, window, Text, destroy, Vec3
from player import Snake
from food import Food
from world import WorldGrid
from camera import SnakeCamera
from config import GRID_SIZE, BACKGROUND_COLOR, FULLSCREEN

# --- Global Game Objects ---
app = Ursina(fullscreen=FULLSCREEN)
grid = WorldGrid()
snake = Snake()
food = Food()
camera_controller = SnakeCamera(snake)
score = 0
score_text = Text(text=f"Score: {score}", position=(-0.85, 0.45), scale=2)
game_over_text = Text(text="", origin=(0, 0), scale=3)

# --- Game Window ---
window.color = BACKGROUND_COLOR

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

def update():
    """
    This function is called every frame by Ursina.
    """
    global score
    
    if snake.direction.length() > 0: # If game is active
        snake.apply_turn() # Apply any buffered turns

        # Check for game over *before* moving
        if snake.will_collide(GRID_SIZE):
            game_over_text.text = "Game Over\n(Press 'r' to restart)"
            game_over_text.color = window.color.invert()
            snake.direction = Vec3(0, 0, 0) # Stop the snake
            return # Stop the rest of the update function

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
