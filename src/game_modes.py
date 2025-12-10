# Defines different game modes.
from ursina import Entity, Text, Button, color, camera, application

class MainMenu(Entity):
    def __init__(self, start_game_callback):
        super().__init__(parent=camera.ui)
        self.start_callback = start_game_callback
        
        # Background
        self.bg = Entity(parent=self, model='quad', scale=(10, 10), color=color.black66, z=1)
        
        # Title
        self.title = Text(text='3D SNAKE', parent=self, scale=4, y=0.3, origin=(0,0), color=color.green)
        
        # Buttons
        self.btn_classic = Button(
            text='Classic Mode\n(Solo)', 
            color=color.azure, 
            scale=(0.4, 0.1), 
            position=(0, 0.05), 
            parent=self
        )
        self.btn_classic.on_click = lambda: self.on_mode_select('classic')
        
        self.btn_ai = Button(
            text='Survival Mode\n(vs AI)', 
            color=color.orange, 
            scale=(0.4, 0.1), 
            position=(0, -0.1), 
            parent=self
        )
        self.btn_ai.on_click = lambda: self.on_mode_select('ai')

        self.btn_quit = Button(
            text='Quit', 
            color=color.red, 
            scale=(0.3, 0.08), 
            position=(0, -0.25), 
            parent=self
        )
        self.btn_quit.on_click = application.quit

    def on_mode_select(self, mode):
        # Hide the menu
        self.enabled = False
        # Call the start function in main.py with the selected mode
        self.start_callback(mode)

    def show(self):
        self.enabled = True