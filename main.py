from winprob_utils import openDriver, createTensor
from plot_utils import plot_game_from_tensor
import numpy as np #type:ignore

driver = openDriver()

flat_regular_ids = np.load("flat_regular_ids.npy")
flat_playoff_ids = np.load("flat_playoff_ids.npy")
# print(flat_playoff_ids)

# createTensor(flat_playoff_ids,"playoffs_winprob.npy",driver)
createTensor(flat_regular_ids,"regseason_winprob.npy",driver)


driver.quit()