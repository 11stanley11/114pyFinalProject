#score keeping
import json
import os

# Define where the file is saved
SCORE_FILE = "highscores.json"

def load_scores():
    """
    Reads the high scores from the JSON file.
    Returns a list of dictionaries: [{'name': 'Player', 'score': 10}, ...]
    """
    if not os.path.exists(SCORE_FILE):
        # Return some default dummy scores if file doesn't exist
        return [
            {'name': 'SnakeMaster', 'score': 10},
            {'name': 'Python', 'score': 5},
            {'name': 'Novice', 'score': 2}
        ]
    try:
        with open(SCORE_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_new_score(name, score):
    """
    Adds a new score, sorts the list, keeps top 10, and saves to file.
    """
    scores = load_scores()
    scores.append({'name': name, 'score': score})
    
    # Sort by score descending (highest first)
    scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Keep only top 10
    scores = scores[:10]
    
    try:
        with open(SCORE_FILE, 'w') as f:
            json.dump(scores, f)
    except Exception as e:
        print(f"Error saving score: {e}")

def is_high_score(score):
    """
    Checks if a score is good enough to be on the leaderboard.
    """
    scores = load_scores()
    # If we have fewer than 10 scores, any score is a high score
    if len(scores) < 10:
        return True
    # Otherwise, beat the lowest score
    return score > scores[-1]['score']