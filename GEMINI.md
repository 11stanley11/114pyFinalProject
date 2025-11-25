# Agent Instructions
This file is used to track the development process. Please update it with changes and progress.

# Gemini Project Tracker

This file is used by the Gemini agent to track the development process of the 3D Snake Game.

## Current Task

**Camera adjusted to isometric view.**

### Sub-tasks:
- [x] Adjusted camera to a more isometric view.

---

## Changelog

### Bug Fixes and Camera Adjustments
- Fixed inverted 'a' and 'd' controls.
- Fixed head marker not being removed on restart.
- Adjusted camera for a more tilted and centered view.
- Adjusted camera to a more isometric view.

### UI and Camera
- Removed key input UI.
- Added a marker to the snake's head.
- Adjusted camera to a more top-down view.
- Fixed a bug with `look_at` method.

### Initial Project Setup
- Read `README.md` and `requirements.txt`.
- Created `GEMINI.md`.
- Populated `src/config.py` with basic settings.
- Created a `Snake` class in `src/player.py`.
- Created a `Food` class in `src/food.py`.
- Implemented the main game loop in `src/main.py`.
- Ensured the game is runnable and fixed initial import errors.

### Playability Improvements
- Made the game controllable by fixing the `update` loop scope.
- Added a 3D grid to visualize the play area.
- Replaced grid lines with grid joints for better visibility.
- Created a dynamic camera in `src/camera.py` to follow the snake.
- Added a restart feature ('r' key on game over).
- Corrected various `IndentationError` and `TypeError` issues.

### Gameplay Adjustments
- Increased camera distance for a better view.
- Reverted to a more direct movement input system.
- Increased the snake's starting length to 3.
- Decreased snake speed for easier gameplay.
- Confirmed game runs and changes are applied.