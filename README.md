# 3D Snake Game

A 3D snake game built with Python and the Ursina engine. This project extends the classic snake game into a three-dimensional world, incorporating modern features like AI opponents and multiple game modes.

## Features

- **3D Gameplay:** Navigate a snake in a fully 3D environment.
- **Five Directions of Movement:** Control the snake's movement forward, left, right, up, and down.
- **Levels & Obstacles:** Progress through different levels with unique challenges and obstacles.
- **Game Modes:** Experience various modes of play.
- **AI Opponents:** Compete against AI-controlled snakes, inspired by slither.io.
- **UI:** A user-friendly interface for game interaction.

## Project Structure

```
.
├── assets/             # Game assets (models, textures, sounds)
├── src/                # Source code
│   ├── __init__.py     # Makes 'src' a Python package
│   ├── main.py         # Main entry point of the game
│   ├── config.py       # Game configuration (e.g., screen resolution, colors)
│   ├── player.py       # Player-controlled snake
│   ├── ai.py           # AI-controlled snakes
│   ├── food.py         # Food for the snake
│   ├── world.py        # Game world, levels, and obstacles
│   ├── ui.py           # User interface elements
│   └── game_modes.py   # Different game modes
├── tests/              # Unit tests
│   ├── __init__.py
│   └── ...
├── README.md           # This file
└── requirements.txt    # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.x

### Installation

1.  Clone the repository:
    ```sh
    git clone <repository-url>
    cd 3d-snake-game
    ```
2.  Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

### Running the Game

```sh
python src/main.py
```

## Contributing

Contributions are welcome! Please feel free to fork the repository and submit a pull request.
