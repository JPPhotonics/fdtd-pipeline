import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from scipy.interpolate import CubicSpline

current_directory = os.getcwd()
sys.path.append(current_directory)

from helper_functions.tidy3d.data_analysis import read_mode_monitor_from_file

lumapi_path = r"C:\Program Files\Lumerical\v251\api\python"
sys.path.append(lumapi_path)
sys.path.append(os.path.dirname(__file__))
import lumapi

def read_lumerical_output(fname):
    project = lumapi.FDTD()
    project.load(fname)
    temp = project.getresult("FDTD::ports::o2", "expansion for port monitor")
    T_net = temp["T_net"]
    wav = temp["lambda"][:,0]

    wav = wav*1e6
    wav = np.flip(wav)

    T_TE0 = T_net[:, 0]
    T_TE0 = T_TE0/np.max(T_TE0)
    T_TE0 = np.flip(T_TE0)

    return wav, T_TE0

def read_tidy3d_output(fname):
    wav, T = read_mode_monitor_from_file(fname, "o2 mode")
    wav = np.flip(wav)
    
    T = T[:, 0].values
    T = T/np.max(T)
    T = np.flip(T)

    return wav, T

def find_FWHM(wav, T):

    # interpolate to 1000 points
    wav_interp = np.linspace(np.min(wav), np.max(wav), 1000)
    T_interp = CubicSpline(wav, T)

    plt.plot(wav_interp, T_interp(wav_interp), '-', color='orange')
    plt.plot(wav, T, 'o', color='blue')
    
    # find the half level
    mini = np.min(T_interp(wav_interp))
    half_level = 0.5 + 0.5*mini

    plt.hlines(half_level, np.min(wav_interp), np.max(wav_interp), color='black', linewidth=2)
    
    # find the indices of the half level
    half_level_indices = [0, 0]
    # first
    for ii in range(len(wav_interp)):
        if T_interp(wav_interp[ii]) < half_level and T_interp(wav_interp[ii-1]) > half_level and wav_interp[ii] > np.min(wav)+0.001 and wav_interp[ii] < np.max(wav)-0.005:
            half_level_indices[0] = ii
            print(f"First half level index: {half_level_indices[0]}")
            break
    # second
    for ii in range(len(wav_interp)):
        if T_interp(wav_interp[ii]) < half_level and T_interp(wav_interp[ii+1]) > half_level and wav_interp[ii] > np.min(wav)+0.005 and wav_interp[ii] < np.max(wav)-0.005:
            half_level_indices[1] = ii
            print(f"Second half level index: {half_level_indices[1]}")
            break

    # find the FWHM
    print(half_level_indices)
    FWHM = wav_interp[half_level_indices[1]] - wav_interp[half_level_indices[0]]

    # peak wavelength
    peak_idx = int(np.round(np.average(half_level_indices)))
    peak_wav = wav_interp[peak_idx]


    plt.axvspan(
        wav_interp[half_level_indices[0]], 
        wav_interp[half_level_indices[1]], 
        color='red', alpha=0.3)

    plt.plot(peak_wav, T_interp(peak_wav), 'o', color='green')
    
    plt.show()

    return FWHM, peak_wav
    

solver = "tidy3d"
folder = "projects/FDTD_solvers/ring/Data/"+solver+"/sweep_resolution/"
# file = "res25_span20_step5_FDTD.fsp"
file = "res25_span20_step5_results.hdf5"

if solver == "lumerical":
    wav, T = read_lumerical_output(folder+file)
elif solver == "tidy3d":
    wav, T = read_tidy3d_output(folder+file)

FWHM, peak_wav = find_FWHM(wav, T)
print(f"FWHM: {FWHM*1e3:.2f} nm")
print(f"Peak wavelength: {peak_wav*1e3:.2f} nm")

Q = peak_wav/FWHM
print(f"Q factor: {Q:.2f}")
    
    




