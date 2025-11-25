"""
UI elements for the game.
"""
from ursina import Entity, Text, camera, destroy, color

class DirectionHints(Entity):
    def __init__(self, snake):
        super().__init__()
        self.snake = snake
        
        common_props = {'scale': 3, 'origin': (0,0), 'color': color.yellow} # Bigger scale, bright color
        self.w_hint = Text(text='w', **common_props)
        self.a_hint = Text(text='a', **common_props)
        self.s_hint = Text(text='s', **common_props)
        self.d_hint = Text(text='d', **common_props)
        
        self.hints = [self.w_hint, self.a_hint, self.s_hint, self.d_hint]
        
        self.offset = 2.0

    def update(self):
        if not self.snake or not self.snake.body:
            for hint in self.hints:
                hint.enabled = False
            return
            
        for hint in self.hints:
            hint.enabled = True

        head = self.snake.head
        direction = self.snake.direction
        up = self.snake.up
        right = direction.cross(up).normalized()

        self.w_hint.position = head.position + up * self.offset
        self.s_hint.position = head.position - up * self.offset
        self.d_hint.position = head.position + right * self.offset
        self.a_hint.position = head.position - right * self.offset
        
        print(f"Hint w position: {self.w_hint.position}") # DEBUG PRINT

        for hint in self.hints:
            hint.billboard = True

    def __del__(self):
        for hint in self.hints:
            destroy(hint)
