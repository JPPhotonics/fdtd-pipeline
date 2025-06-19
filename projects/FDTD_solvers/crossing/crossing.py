import os
import sys
from datetime import datetime

# add current working directory to system path
current_directory = os.getcwd()
sys.path.append(current_directory)

# import simulation functions for different solvers
from gds_library import pdk_universal
from helper_functions.lumerical.simulate_device import simulate_predefined_gds as lumerical_simulate_predefined_gds
from helper_functions.tidy3d.simulate_device import simulate_predefined_gds as tidy3d_simulate_predefined_gds

# select simulation solver: 'lumerical' or 'tidy3d'
solver = 'lumerical'
# solver = 'tidy3d'

# define simulation parameters
res = 6       # simulation resolution, number of cells per wavelength
span = 20     # wavelength span (nm)
um = 0.001    # convert nanometer to micrometer
mode_idx = 0  # index of the injected mode, Lumerical starts with 1, Tidy3D starts with 0
flag_run_simulation = 1 # Run simulation?

# define file paths and simulation parameters
# path to GDS file ready for simulation
gds_file_path = os.path.join(
    current_directory, 'gds_library', 'cells_from_gds', 'gdsfactory_generic_pdk',
    'crossing.gds'
)
# path to output file
output_dir = os.path.join(
    current_directory, 'projects', 'FDTD_solvers', 'crossing', 'Data', solver,
    f'sweep_resolution/res{res}_span{span}_step5'
)
# task name for Tidy3D
task_name = f'CROSS_res{res}_span{span}_step5_{datetime.now().strftime("%Y%m%d%H%M%S")}'

# define the simulation parameter dictionary
p = dict(
    # wavelength span in micrometer
    wav_span = span * um,
    # spatial resolution, number of cells per wavelength
    resolution = res,
    # path to the GDS file
    predefined_gds = gds_file_path,
    # output file path
    file_name = output_dir,
    # task name for Tidy3D
    task_name = task_name,
    # index of the injected mode
    mode_idx = mode_idx,
    # run simulation?
    flag_run_simulation = flag_run_simulation,
    # Control the top cladding: False, keep SiO2; True, change to Si3N4.
    change_cladding = False,
)

# Run the simulation using the selected solver
if solver == 'lumerical':
    lumerical_simulate_predefined_gds(parameters=p)
if solver == 'tidy3d':
    tidy3d_simulate_predefined_gds(parameters=p)
