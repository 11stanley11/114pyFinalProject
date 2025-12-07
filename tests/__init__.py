from ursina import *

app = Ursina()

def input(key):
    print(f'Detected input: {key}')

app.run()