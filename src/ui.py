"""
UI elements for the game.
"""

from ursina import Ursina, Entity, Text, Button, camera, destroy, window
from ursina.prefabs.window_panel import WindowPanel

HIGH_SCORE_FILE = "highscore.txt"

def get_high_score():
    """
    Reads the high score from the highscore.txt file.
    If the file doesn't exist, it returns 0.
    """
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0

def set_high_score(score):
    """
    Writes the new high score to the highscore.txt file.
    """
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))

class GameOverUI(Entity):
    def __init__(self, current_score, restart_func, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        high_score = get_high_score()
        if current_score > high_score:
            set_high_score(current_score)
            high_score = current_score
        
        self.window = WindowPanel(
            title='Game Over',
            content=[
                Text(f'Score: {current_score}'),
                Text(f'High Score: {high_score}'),
                Button('Restart', on_click=restart_func),
                Text("(Press 'r' to restart)", origin=(0, -2))
            ],
            popup=True,
            enabled=True
        )

    def close(self):
        destroy(self.window)
        destroy(self)