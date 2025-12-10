#score keeping
import json
import os

# Define where the file is saved
SCORE_FILE = "highscores.json"

def get_empty_structure():
    return {
        'classic': [],
        'ai': []
    }

def load_all_scores():
    if not os.path.exists(SCORE_FILE):
        return get_empty_structure()
    try:
        with open(SCORE_FILE, 'r') as f:
            data = json.load(f)
            # Backward compatibility: if list, wrap it in 'classic'
            if isinstance(data, list):
                return {
                    'classic': data,
                    'ai': get_empty_structure()['ai']
                }
            return data
    except:
        return get_empty_structure()

def load_scores(mode='classic'):
    """
    Reads the high scores for a specific mode from the JSON file.
    Returns a list of dictionaries: [{'name': 'Player', 'score': 10}, ...]
    """
    data = load_all_scores()
    return data.get(mode, [])

def save_new_score(name, score, mode='classic'):
    """
    Updates the score for a player if the new score is higher than their existing record.
    If the player is new, adds them.
    Maintains top 10 scores per mode.
    Ignores 'Guest' players.
    """
    if name == "Guest":
        return

    data = load_all_scores()
    
    # Ensure the mode key exists
    if mode not in data:
        data[mode] = []

    scores = data[mode]
    
    # Check if player exists
    player_found = False
    for entry in scores:
        if entry['name'] == name:
            player_found = True
            if score > entry['score']:
                entry['score'] = score
            else:
                # New score is not higher, so we don't update
                return
            break
            
    if not player_found:
        scores.append({'name': name, 'score': score})
    
    # Sort by score descending (highest first)
    scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Keep only top 10
    scores = scores[:10]
    data[mode] = scores
    
    try:
        with open(SCORE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving score: {e}")

def is_high_score(score, mode='classic'):
    """
    Checks if a score is good enough to be on the leaderboard for the given mode.
    """
    scores = load_scores(mode)
    # If we have fewer than 10 scores, any score is a high score
    if len(scores) < 10:
        return True
    # Otherwise, beat the lowest score
    return score > scores[-1]['score']