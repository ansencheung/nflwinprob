from winprob_utils import openDriver, createTensor
from plot_utils import plot_game_from_tensor
from getID import getIds
import numpy as np  #type: ignore

driver = openDriver()


all_regular_season_ids = []
all_playoff_ids = []

for year in range(2016, 2025):  # 2016 to 2024 inclusive
    # 🔁 Regular season: Weeks 1–18
    for week in range(1, 19):
        url = f"https://www.espn.com/nfl/scoreboard/_/week/{week}/year/{year}/seasontype/2"
        regular_ids = getIds(driver,url)
        print(regular_ids)
        all_regular_season_ids.append(regular_ids)

    # 🔁 Playoffs: Weeks 1–5 (excluding 4)
    for week in [1, 2, 3, 5]:
        url = f"https://www.espn.com/nfl/scoreboard/_/week/{week}/year/{year}/seasontype/3"
        playoff_ids = getIds(driver,url)
        print(playoff_ids)
        all_playoff_ids.append(playoff_ids)

    total_regular = sum(len(ids) for ids in all_regular_season_ids[-18:])
    total_playoff = sum(len(ids) for ids in all_playoff_ids[-4:])
    print(f"{year} — Regular Season: {total_regular} games, Playoffs: {total_playoff} games")


# Flatten the list of lists into one flat list
flat_regular_ids = [id for sublist in all_regular_season_ids for id in sublist]
flat_playoff_ids = [id for sublist in all_playoff_ids for id in sublist]

np.save("flat_regular_ids.npy", np.array(flat_regular_ids))
np.save("flat_playoff_ids.npy", np.array(flat_playoff_ids))


print(len(flat_playoff_ids))
print(len(flat_regular_ids))

driver.quit()