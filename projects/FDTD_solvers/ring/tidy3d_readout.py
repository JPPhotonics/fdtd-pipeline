import os
import sys
import numpy as np

current_directory = os.getcwd()
sys.path.append(current_directory)

from helper_functions.tidy3d.data_analysis import read_mode_monitor_from_file

fname = "projects/FDTD_solvers/ring/Data/tidy3d/sweep_resolution/"
file = "res20_span50_step5_results.hdf5"

wav, T = read_mode_monitor_from_file(fname+file, "o2 mode")

T = T[:,0]
T = T/np.max(T)

for ii in range(len(T)):
    print(T[ii].values)





