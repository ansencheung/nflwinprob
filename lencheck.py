import numpy as np #type: ignore

loaded_data_regs = np.load('regseason_winprob.npy', allow_pickle=True)
loaded_data_po  = np.load('playoffs_winprob.npy', allow_pickle=True)
loaded_ids_regs = np.load("flat_regular_ids.npy")
loaded_ids_po = np.load("flat_playoff_ids.npy")

print(loaded_ids_po.shape)
print(loaded_data_po.shape)
print(loaded_ids_regs.shape)
print(loaded_data_regs.shape)
