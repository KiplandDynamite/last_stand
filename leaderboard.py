import os

LEADERBOARD_FILE = "leaderboard.txt"

# Ensure leaderboard file exists
if not os.path.exists(LEADERBOARD_FILE):
    with open(LEADERBOARD_FILE, "w") as f:
        f.write("Isaac,4,2300\nKippyD,9,14000\nTaban,6,6950\n")


def load_leaderboard():
    """Loads leaderboard and returns sorted list of top scores."""
    scores = []
    with open(LEADERBOARD_FILE, "r") as f:
        for line in f.readlines():
            parts = line.strip().split(",")

            # Ensure data is formatted correctly (name, time, score)
            if len(parts) == 3:
                name, wave, score = parts
                try:
                    scores.append((name.strip(), int(wave.strip()), int(score.strip())))
                except ValueError:
                    print(f"Skipping malformed entry: {line.strip()}")  # Debugging message

    return sorted(scores, key=lambda x: x[2], reverse=True)


def save_leaderboard(name, score, waves):
    """Saves a new player score, sorts the leaderboard, and keeps the top 10 scores."""
    scores = load_leaderboard()
    scores.append((name.strip(), int(waves), int(score)))  # Changed 'time' to 'waves'
    scores = sorted(scores, key=lambda x: x[2], reverse=True)[:10]  # Sort by highest score

    with open(LEADERBOARD_FILE, "w") as f:
        for entry in scores:
            f.write(f"{entry[0]},{entry[1]},{entry[2]}\n")  # Keep saving format consistent

