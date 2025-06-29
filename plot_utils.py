import matplotlib.pyplot as plt #type: ignore
import numpy as np #type: ignore


def plot_game_from_tensor(tensor, game_index):
    """
    Plot win probability over time for the nth unique game in the tensor.

    Parameters:
    - tensor: np.array with shape (N, 3) where columns are [time_sec, win_prob, game_id]
    - game_index: the index of the unique game to plot (e.g. 0, 1, ..., 155)
    """
    # Get list of unique game IDs
    unique_game_ids = np.unique(tensor[:, 2])
    
    if game_index >= len(unique_game_ids):
        print(f"Error: game_index {game_index} is out of range. Only {len(unique_game_ids)} games available.")
        return
    
    # Get the game ID corresponding to the requested index
    game_id = unique_game_ids[game_index]

    # Filter tensor to only that game's data
    game_data = tensor[tensor[:, 2] == game_id]

    # Sort by time
    game_data = game_data[game_data[:, 0].argsort()]

    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(game_data[:, 0], game_data[:, 1], marker='o', linestyle='-')
    plt.title(f"Win Probability Over Time (Game ID: {int(game_id)})")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Win Probability (%)")
    plt.xlim(0, 3600)
    plt.ylim(0, 100)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
