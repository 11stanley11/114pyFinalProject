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

class GameHUD(Entity):
    def __init__(self, player_name, current_mode, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)
        self.player_name = player_name
        self.current_mode = current_mode
        self.high_score = 0
        self.margin = 0.025 # Distance from the edge
        
        # Current Score (Top Left)
        # Position will be set in update()
        self.score_text = Text(text='Score: 0', origin=(-0.5, 0.5), scale=1.5, color=color.white, font=REGULAR_FONT, parent=self)
        
        # High Score (Top Right)
        if player_name != "Guest":
            scores = leaderboard.load_scores(current_mode)
            for entry in scores:
                if entry['name'] == player_name:
                    self.high_score = entry['score']
                    break
            
            self.high_score_text = Text(text=f'High Score: {self.high_score}', origin=(0.5, 0.5), scale=1.5, color=color.white, font=REGULAR_FONT, parent=self)
        else:
            self.high_score_text = None

        # Run one update immediately to set initial positions
        self.update()

    def update(self):
        # Dynamically anchor to window corners
        # window.top_left is usually (-aspect_ratio/2, 0.5)
        
        if self.score_text:
            self.score_text.position = (window.top_left.x + self.margin, window.top_left.y - self.margin)
            
        if self.high_score_text:
            self.high_score_text.position = (window.top_right.x - self.margin, window.top_right.y - self.margin)

    def update_score(self, current_score):
        self.score_text.text = f'Score: {current_score}'
        
        if self.high_score_text:
            if current_score > self.high_score:
                self.high_score_text.text = f'High Score: {current_score}'
                self.high_score_text.color = color.yellow
            else:
                self.high_score_text.color = color.white

class GameOverUI(Entity):
    def __init__(self, player_name, score, current_mode, restart_callback, menu_callback, **kwargs):
        super().__init__(parent=camera.ui, ignore_paused=True, **kwargs)
        
        self.restart_callback = restart_callback
        self.menu_callback = menu_callback

        # Background Overlay
        self.bg = Entity(parent=self, model='quad', scale=(20, 10), color=color.black66, z=11)

        # --- Central Panel ---
        self.panel = Entity(parent=self, model='quad', scale=(0.5, 0.4), color=color.black33, z=10) # Adjusted z for layering
        # Removed self.panel_border as requested

        # Title
        Text(text='GAME OVER', parent=self.panel, scale=5.5, y=0.2, origin=(0,0), color=color.red, font=BOLD_FONT)
        
        # Player Name 
        Text(text=f'Player: {player_name}', parent=self.panel, scale=2, y=0.05, origin=(0,0), color=color.azure, font=REGULAR_FONT)
        
        # Score
        Text(text=f'Score: {score}', parent=self.panel, scale=2.3, position=(-0.2, -0.05), origin=(0,0), color=color.white, font=REGULAR_FONT)

        # Highscore (Fetch from leaderboard)
        scores = leaderboard.load_scores(current_mode)
        player_highscore = score # Default to current if not found
        for entry in scores:
            if entry['name'] == player_name:
                player_highscore = entry['score']
                break
        
        # High Score
        Text(text=f'High Score: {player_highscore}', parent=self.panel, scale=2.3, position=(0.2, -0.05), origin=(0,0), color=color.gold, font=REGULAR_FONT)

        # Buttons (adjusted y position)
        # Restart
        self.btn_restart = Button(text='Restart', color=color.gray, text_color=color.white, scale=(0.3, 0.1), position=(-0.2, -0.20), highlight_text_color=color.green, parent=self.panel, font=ITALIC_FONT)
        self.btn_restart.on_click = self.restart_callback
        self.btn_restart.text_entity.font = ITALIC_FONT
        # Hint
        Text(text='(Press R)', parent=self.panel, scale=1.3, position=(-0.2, -0.275), origin=(0,0), color=color.light_gray, font=REGULAR_FONT)

        # Menu
        self.btn_menu = Button(text='Main Menu', color=color.azure, scale=(0.3, 0.1), position=(0.2, -0.20), parent=self.panel, font=REGULAR_FONT)
        self.btn_menu.on_click = self.menu_callback
        self.btn_menu.text_entity.font = REGULAR_FONT
        # Hint
        Text(text='(Press M)', parent=self.panel, scale=1.3, position=(0.2, -0.275), origin=(0,0), color=color.light_gray, font=REGULAR_FONT)
        # --- Leaderboard Panel (Bottom Left) ---
        self.leaderboard_container = Entity(parent=self, position=(-0.65, -0.2), z=-10) # Adjusted z for layering
        Entity(parent=self.leaderboard_container, model='quad', scale=(0.3, 0.4), color=color.black50, origin=(0,0))
        
        Text(text='Leaderboard', parent=self.leaderboard_container, scale=1.2, y=0.15, origin=(0,0), color=color.gold, font=BOLD_FONT)
        
        # Headers
        Text(text='Name', parent=self.leaderboard_container, scale=0.8, position=(-0.09, 0.10), origin=(0,0), color=color.light_gray, font=REGULAR_FONT)
        Text(text='Score', parent=self.leaderboard_container, scale=0.8, position=(0.08, 0.10), origin=(0,0), color=color.light_gray, font=REGULAR_FONT)
        Entity(parent=self.leaderboard_container, model='quad', scale=(0.25, 0.002), y=0.075, color=color.gray)

        # Rows
        start_y = 0.065
        row_height = 0.025
        # Sort and limit scores just in case (though load_scores should handle it)
        scores = sorted(scores, key=lambda x: x['score'], reverse=True)[:10]

        for i in range(10):
            y_pos = start_y - (i * row_height)
            name_txt = "-"
            score_txt = "-"
            col = color.white
            
            if i < len(scores):
                entry = scores[i]
                name_txt = entry['name'][:10]
                score_txt = str(entry['score'])
                if entry['name'] == player_name and player_name != "Guest":
                    col = color.azure
            
            Text(text=name_txt, parent=self.leaderboard_container, scale=0.75, position=(-0.12, y_pos), origin=(-0.5, 0.5), color=col, font=REGULAR_FONT)
            Text(text=score_txt, parent=self.leaderboard_container, scale=0.75, position=(0.08, y_pos), origin=(0, 0.5), color=col, font=REGULAR_FONT)



class MainMenu(Entity):
    def __init__(self, start_game_callback, quit_callback):
        super().__init__(parent=camera.ui)
        self.start_game_callback = start_game_callback
        self.quit_callback = quit_callback
        
        # Data
        self.modes = [
            {'key': 'classic', 'name': 'Classic Mode', 'desc': 'Classic Snake: Eat and Grow', 'color': color.yellow},
            {'key': 'ai', 'name': 'Survival Mode (Easy)', 'desc': 'Avoid the AI Snake!', 'color': color.orange},
            {'key': 'ai_hard', 'name': 'Survival Mode (Hard)', 'desc': 'Hunter AI: Chases you!', 'color': color.red}
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
        self.btn_play = Button(text='PLAY', color=color.gray, text_size=1.25, scale=(0.175, 0.06), position=(0, -0.2), parent=self, z=-1, highlight_text_color=color.green, font=ITALIC_FONT)
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

        # Quit Button (Bottom Right, right of Settings)
        self.btn_quit = Button(model='quad', texture='../assets/quitIcon.png', scale=(0.045, 0.045), position=(0.75, -0.44), parent=self, z=-1, color=color.white, highlight_color=color.light_gray)
        self.btn_quit.on_click = self.quit_callback

        # --- Settings Panel (Bottom Right) ---
        # Panel Background
        self.settings_panel = Entity(parent=self, position=(0.6, -0.2), enabled=False, z=-2)
        Entity(parent=self.settings_panel, model='quad', scale=(0.35, 0.4), color=color.black66, origin=(0,0))
        
        # Title
        Text(text='Camera & Input Mode', parent=self.settings_panel, scale=0.8, y=0.16, origin=(0,0), color=color.white, font=BOLD_FONT)
        Entity(parent=self.settings_panel, model='quad', scale=(0.3, 0.002), y=0.13, color=color.gray)

        # --- Toggles ---
        self.selected_cam_mode = 'follow' # Default
        self.cam_toggles = {} # To store buttons for visual updating

        # Helper to create rows
        def create_option(key, name, desc, y_pos):
            # Container for click detection
            btn = Button(parent=self.settings_panel, scale=(0.3, 0.1), position=(0, y_pos), color=color.clear, highlight_color=color.black33)
            
            # Text Elements
            t_name = Text(text=name, parent=self.settings_panel, position=(-0.15, y_pos+0.015), origin=(-0.5, 0), scale=1.0, font=REGULAR_FONT, color=color.white)
            t_desc = Text(text=desc, parent=self.settings_panel, position=(-0.15, y_pos-0.015), origin=(-0.5, 0), scale=0.8, font=REGULAR_FONT, color=color.light_gray)
            
            # Indicator (Checkmark/Dot box)
            indicator = Entity(parent=btn, model='quad', scale=(0.05, 0.5), position=(0.45, 0), color=color.dark_gray)
            
            # Store reference
            self.cam_toggles[key] = {'btn': btn, 'indicator': indicator, 'name': t_name}
            
            # Click Handler
            btn.on_click = lambda: self.set_camera_mode(key)

        # create_option('orbital', 'Orbital Cam', 'Rotates around grid + Standard Input', 0.08)
        # create_option('topdown', 'Top Down', 'Bird\'s eye view + Standard Input', -0.02)
        # create_option('follow', 'Follow Cam', 'Classic behind view + Free Roam', -0.12)
        
        create_option('orbital', 'Orbital Cam', 'Rotates around grid', 0.07) # + standard input
        create_option('topdown', 'Top Down', 'Bird\'s eye view', -0.03) # + standard input
        create_option('follow', 'Action Cam', 'Classic behind view', -0.13) # + free roam input

        # Highlight default
        self.update_settings_ui()
        self.update_mode_display()

    def set_camera_mode(self, mode):
        self.selected_cam_mode = mode
        self.update_settings_ui()
        print(f"Selected Mode: {mode}")

    def update_settings_ui(self):
        for key, ui in self.cam_toggles.items():
            if key == self.selected_cam_mode:
                ui['indicator'].color = color.azure
                ui['name'].color = color.azure
            else:
                ui['indicator'].color = color.dark_gray
                ui['name'].color = color.white

    def update_leaderboard(self):
        mode_key = self.modes[self.current_mode_index]['key']
        
        # Map ai_hard to ai for leaderboard purposes so they share scores
        if mode_key == 'ai_hard':
            mode_key = 'ai'
            
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
        self.update_leaderboard()

    def change_mode(self, direction):
        offset = 0.6 
        duration = 0.3
        anim_offset = offset * direction

        ghost = Entity(parent=self, position=self.mode_display.position)
        Text(text=self.mode_name_text.text, parent=ghost, scale=2, origin=(0,0), y=-0.025, color=self.mode_name_text.color, z=-1, font=REGULAR_FONT)
        Text(text=self.mode_desc_text.text, parent=ghost, scale=1, origin=(0,0), y=-0.075, color=self.mode_desc_text.color, z=-1, font=REGULAR_FONT)
        
        ghost.animate_x(ghost.x + anim_offset, duration=duration, curve=curve.out_expo)
        for child in ghost.children:
            child.animate('alpha', 0, duration=duration, curve=curve.out_expo)
            
        destroy(ghost, delay=duration + 0.1)
        
        self.current_mode_index = (self.current_mode_index + direction) % len(self.modes)
        self.update_mode_display()
        
        self.mode_display.x = -anim_offset
        self.mode_display.animate_x(0, duration=duration, curve=curve.out_expo)

        for child in self.mode_display.children:
            child.alpha = 0
            child.animate('alpha', 1, duration=duration, curve=curve.out_expo)

    def next_mode(self):
        self.change_mode(1)

    def prev_mode(self):
        self.change_mode(-1)

    def on_play(self):
        selected_mode_key = self.modes[self.current_mode_index]['key']
        player_name = self.name_input.text
        if not player_name: player_name = "Guest"
        
        # Determine actual game mode and aggression
        actual_mode = selected_mode_key
        is_aggressive = False
        
        if selected_mode_key == 'ai_hard':
            actual_mode = 'ai'
            is_aggressive = True
        elif selected_mode_key == 'ai':
            actual_mode = 'ai'
            is_aggressive = False
            
        self.start_game_callback(actual_mode, player_name, self.selected_cam_mode, is_aggressive)
    
    def toggle_settings(self):
        self.settings_panel.enabled = not self.settings_panel.enabled
