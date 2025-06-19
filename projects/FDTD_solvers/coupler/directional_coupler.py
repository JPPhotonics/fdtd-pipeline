"""
Directional Coupler Simulation Script

This script simulates a directional coupler device using either Lumerical FDTD or Tidy3D.
The simulation can be configured for different resolutions, wavelength spans, and modes.

Author: Zuyang Liu
Date: 2024
"""

import os
import sys
from datetime import datetime
import logging

# Add current working directory to system path
current_directory = os.getcwd()
sys.path.append(current_directory)

# Import simulation functions for different solvers
from gds_library import pdk_universal
from helper_functions.lumerical.simulate_device import simulate_predefined_gds as lumerical_simulate_predefined_gds
from helper_functions.tidy3d.simulate_device import simulate_predefined_gds as tidy3d_simulate_predefined_gds

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main simulation function for directional coupler."""
    
    # Select simulation solver: 'lumerical' or 'tidy3d'
    solver = 'lumerical'
    # solver = 'tidy3d'

    # Define simulation parameters
    res = 6           # simulation resolution, number of cells per wavelength
    span = 20         # wavelength span (nm)
    um = 0.001        # convert nanometer to micrometer
    mode_idx = 0      # index of the injected mode, Lumerical starts with 1, Tidy3D starts with 0
    flag_run_simulation = 1  # Run simulation?

    # Define file paths and simulation parameters
    # Path to GDS file ready for simulation
    gds_file_path = os.path.join(
        current_directory, 'gds_library', 'cells_from_gds', 'gdsfactory_generic_pdk',
        'coupler.gds'
    )
    
    # Path to output file
    output_dir = os.path.join(
        current_directory, 'projects', 'FDTD_solvers', 'coupler', 'Data', solver,
        f'sweep_resolution/res{res}_span{span}_step5'
    )
    
    # Task name for Tidy3D
    task_name = f'DC_res{res}_span{span}_step5_{datetime.now().strftime("%Y%m%d%H%M%S")}'

    # Define the simulation parameter dictionary
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

    logger.info(f"Starting directional coupler simulation with {solver} solver")
    logger.info(f"Resolution: {res} cells/wavelength, Wavelength span: {span} nm")
    logger.info(f"GDS file: {gds_file_path}")

    try:
        # Run the simulation using the selected solver
        if solver == 'lumerical':
            results = lumerical_simulate_predefined_gds(parameters=p)
        elif solver == 'tidy3d':
            results = tidy3d_simulate_predefined_gds(parameters=p)
        else:
            raise ValueError(f"Unknown solver: {solver}. Use 'lumerical' or 'tidy3d'")
        
        if results:
            logger.info("Simulation completed successfully")
        else:
            logger.info("Simulation completed (no results returned)")
            
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise

if __name__ == "__main__":
    main()
