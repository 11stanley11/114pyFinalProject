"UI elements for the game."

from ursina import Ursina, Entity, Text, Button, camera, destroy, window, color, invoke, application, Circle, curve, Quad, InputField
from ursina.prefabs.window_panel import WindowPanel
import leaderboard

REGULAR_FONT = '../assets/MinecraftRegular-Bmg3.otf'
BOLD_FONT = '../assets/MinecraftBold-nMK1.otf'
ITALIC_FONT = '../assets/MinecraftItalic-R8Mo.otf'
BOLDITALIC_FONT = '../assets/MinecraftBoldItalic-1y1e.otf'
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
                Text(f'Score: {current_score}', font=REGULAR_FONT),
                Text(f'High Score: {high_score}', font=REGULAR_FONT),
                Button('Restart', on_click=restart_func, font=REGULAR_FONT),
                Text("(Press 'r' to restart)", origin=(0, -2), font=REGULAR_FONT)
            ],
            popup=True,
            enabled=True
        )


class MainMenu(Entity):
    def __init__(self, start_game_callback, quit_callback):
        super().__init__(parent=camera.ui)
        self.start_game_callback = start_game_callback
        self.quit_callback = quit_callback
        
        # Data
        self.modes = [
            {'key': 'classic', 'name': 'Classic Mode', 'desc': 'Classic Snake: Eat and Grow', 'color': color.yellow},
            {'key': 'ai', 'name': 'Survival Mode', 'desc': 'Avoid the AI Snake!', 'color': color.orange}
        ]
        self.current_mode_index = 0

        # Background
        self.bg = Entity(parent=self, model='quad', scale=(20, 10), color=color.black66, z=10)
        
        # Title (Top of the center group)
        self.title = Text(text='3D SNAKE', parent=self, scale=6, y=0.2, origin=(0,0), color=color.white, z=-1, font=BOLD_FONT)

        # Mode Panel (Background for the mode selector)
        self.mode_panel = Entity(parent=self, model='quad', scale=(0.7, 0.2), position=(0, -0.05), color=color.black33, z=1)

        # Mode Selector Area (Centered)
        self.mode_label = Text(text='MODE', parent=self, scale=1.5, position=(0, 0.075), origin=(0,0), color=color.light_gray, z=-1, font=REGULAR_FONT)
        
        # Container for the mode display
        self.mode_display = Entity(parent=self, position=(0, 0))
        
        # Mode Name
        self.mode_name_text = Text(text='', parent=self.mode_display, scale=2, origin=(0,0), y=-0.025, color=color.azure, z=-1, font=REGULAR_FONT)
        # Mode Description
        self.mode_desc_text = Text(text='', parent=self.mode_display, scale=1, origin=(0,0), y=-0.075, color=color.white, z=-1, font=REGULAR_FONT)

        # Navigation Buttons (Aligned with mode display)
        self.btn_prev = Button(model=Circle(resolution=3), color=color.azure, scale=(0.04, 0.03), rotation_z=-90, position=(-0.375, -0.05), parent=self, z=-1)
        self.btn_prev.on_click = self.prev_mode
        
        self.btn_next = Button(model=Circle(resolution=3), color=color.azure, scale=(0.04, 0.03), rotation_z=90, position=(0.375, -0.05), parent=self, z=-1)
        self.btn_next.on_click = self.next_mode

        # Play Button (Bottom of the center group)
        self.btn_play = Button(text='PLAY', color=color.gray, scale=(0.15, 0.04), position=(0, -0.175), parent=self, z=-1, highlight_text_color=color.green, font=ITALIC_FONT)
        self.btn_play.on_click = self.on_play
        # Explicitly set font and color for the button's text entity
        self.btn_play.text_entity.font = ITALIC_FONT
        self.btn_play.text_entity.color = color.white

        # Leaderboard Display (Bottom Left)
        self.leaderboard_container = Entity(parent=self, position=(-0.65, -0.2), z=-1)
        # Background for leaderboard
        Entity(parent=self.leaderboard_container, model='quad', scale=(0.3, 0.4), color=color.black50, origin=(0,0))
        
        Text(text='Leaderboard', parent=self.leaderboard_container, scale=1.2, y=0.15, origin=(0,0), color=color.gold, font=BOLD_FONT)
        
        # Column Headers
        Text(text='Name', parent=self.leaderboard_container, scale=0.8, position=(-0.09, 0.10), origin=(0,0), color=color.light_gray, font=REGULAR_FONT)
        Text(text='Score', parent=self.leaderboard_container, scale=0.8, position=(0.08, 0.10), origin=(0,0), color=color.light_gray, font=REGULAR_FONT)
        
        # Divider
        Entity(parent=self.leaderboard_container, model='quad', scale=(0.25, 0.002), y=0.075, color=color.gray)
        
        # Leaderboard Content
        # Use separate text entities for each row to allow individual highlighting
        self.lb_entries = []
        start_y = 0.065
        row_height = 0.025
        
        for i in range(10):
            y_pos = start_y - (i * row_height)
            # Name Text
            t_name = Text(text='-', parent=self.leaderboard_container, scale=0.75, position=(-0.12, y_pos), origin=(-0.5, 0.5), font=REGULAR_FONT)
            # Score Text
            t_score = Text(text='-', parent=self.leaderboard_container, scale=0.75, position=(0.08, y_pos), origin=(0, 0.5), font=REGULAR_FONT)
            self.lb_entries.append((t_name, t_score))

        # Player Name Input (Above Leaderboard)
        # Leaderboard BG left edge is at -0.65 - (0.3/2) = -0.80
        self.name_label = Text(text='Currently playing as:', parent=self, position=(-0.79, 0.06), scale=1, origin=(-0.5, 0), color=color.light_gray, font=REGULAR_FONT)
        
        # Position InputField to the right of the label
        self.name_input = InputField(default_value='Guest', parent=self, position=(-0.675, 0.03), scale=(0.25, 0.04), color=color.clear, text_color=color.white, active=False, font=REGULAR_FONT)
        # Force font application on internal TextField text_entity and adjust text scale
        if hasattr(self.name_input, 'text_field') and hasattr(self.name_input.text_field, 'text_entity'):
            self.name_input.text_field.text_entity.font = REGULAR_FONT
            self.name_input.text_field.text_entity.scale = 0.9 # Adjust text size inside the input field
            
        # Update leaderboard when name changes to apply highlighting
        self.name_input.on_value_changed = lambda: self.update_leaderboard()

        # Settings Button (Bottom Right)
        self.btn_settings = Button(model='quad', texture='../assets/settingsIcon.png', scale=(0.06, 0.06), position=(0.69, -0.44), parent=self, z=-1, color=color.white, highlight_color=color.light_gray)
        self.btn_settings.on_click = self.toggle_settings

        # Settings Panel (Hidden by default)
        self.settings_panel = Entity(parent=self, enabled=False, z=-2)
        Entity(parent=self.settings_panel, model='quad', scale=(0.8, 0.6), color=color.dark_gray)
        Text(text='Settings Panel\n(Work in Progress)', parent=self.settings_panel, origin=(0,0), scale=2, font=REGULAR_FONT)
        self.btn_close_settings = Button(text='Close', parent=self.settings_panel, scale=(0.2, 0.05), y=-0.2, color=color.red, font=REGULAR_FONT)
        self.btn_close_settings.on_click = self.toggle_settings

        # Quit Button (Bottom Right, right of Settings)
        self.btn_quit = Button(model='quad', texture='../assets/quitIcon.png', scale=(0.045, 0.045), position=(0.75, -0.44), parent=self, z=-1, color=color.white, highlight_color=color.light_gray)
        self.btn_quit.on_click = self.quit_callback

        self.update_mode_display()

    def update_leaderboard(self):
        mode_key = self.modes[self.current_mode_index]['key']
        scores = leaderboard.load_scores(mode_key)
        
        # Limit to top 10
        scores = scores[:10]
        
        current_player = self.name_input.text
        
        for i in range(10):
            t_name, t_score = self.lb_entries[i]
            
            if i < len(scores):
                entry = scores[i]
                t_name.text = entry['name'][:10]
                t_score.text = str(entry['score'])
                
                # Highlight if name matches current input and is not Guest
                if current_player != "Guest" and entry['name'] == current_player:
                    t_name.color = color.azure
                    t_score.color = color.azure
                else:
                    t_name.color = color.white
                    t_score.color = color.white
            else:
                t_name.text = "-"
                t_score.text = "-"
                t_name.color = color.white
                t_score.color = color.white

    def update_mode_display(self):
        mode_data = self.modes[self.current_mode_index]
        self.mode_name_text.text = mode_data['name']
        self.mode_desc_text.text = mode_data['desc']
        self.mode_name_text.color = mode_data['color']
        # Update image here if we had textures: self.mode_image.texture = mode_data['img']
        self.update_leaderboard()

    def change_mode(self, direction):
        # direction: 1 = Next, -1 = Prev
        offset = 0.6 
        duration = 0.3
        
        # Calculate animation offset based on direction
        anim_offset = offset * direction

        # Ghost for the outgoing text (Visual Copy)
        ghost = Entity(parent=self, position=self.mode_display.position)
        Text(text=self.mode_name_text.text, parent=ghost, scale=2, origin=(0,0), y=-0.025, color=self.mode_name_text.color, z=-1, font=REGULAR_FONT)
        Text(text=self.mode_desc_text.text, parent=ghost, scale=1, origin=(0,0), y=-0.075, color=self.mode_desc_text.color, z=-1, font=REGULAR_FONT)
        
        # Animate ghost exiting
        ghost.animate_x(ghost.x + anim_offset, duration=duration, curve=curve.out_expo)
        for child in ghost.children:
            child.animate('alpha', 0, duration=duration, curve=curve.out_expo)
            
        destroy(ghost, delay=duration + 0.1)
        
        # Update real data
        self.current_mode_index = (self.current_mode_index + direction) % len(self.modes)
        self.update_mode_display()
        
        # Teleport incoming to start position and animate in
        self.mode_display.x = -anim_offset
        self.mode_display.animate_x(0, duration=duration, curve=curve.out_expo)

        # Animate incoming fade-in
        for child in self.mode_display.children:
            child.alpha = 0
            child.animate('alpha', 1, duration=duration, curve=curve.out_expo)

    def next_mode(self):
        self.change_mode(1)

    def prev_mode(self):
        self.change_mode(-1)

    def on_play(self):
        selected_mode = self.modes[self.current_mode_index]['key']
        player_name = self.name_input.text
        if not player_name: player_name = "Guest"
        self.start_game_callback(selected_mode, player_name)
    
    def toggle_settings(self):
        self.settings_panel.enabled = not self.settings_panel.enabled
