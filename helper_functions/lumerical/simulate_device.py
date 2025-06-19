from datetime import datetime
import os
import gdsfactory as gf
import json
import logging
from typing import Dict, Any, Optional

from helper_functions.generic.misc import write_to_json, validate_file_path, ensure_directory_exists
from helper_functions.lumerical.initiate_fdtd import fdtd_from_gds

logger = logging.getLogger(__name__)

def simulate_predefined_gds(parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Initialize and run 3D FDTD simulation of a device defined in a GDS file.
    
    Uses layer stack information from the PDK and supports both Lumerical FDTD
    and Tidy3D solvers. The function handles GDS import, material assignment,
    simulation setup, and result extraction.

    Args:
        parameters: Dictionary containing simulation parameters including:
            - wavelength: Center wavelength in micrometers
            - wav_span: Wavelength span in micrometers  
            - wav_step: Wavelength step size in micrometers
            - resolution: Spatial resolution (cells per wavelength)
            - temperature: Simulation temperature in Kelvin
            - predefined_gds: Path to the GDS file
            - material_type: Material library type ("universal", "VisPDK", etc.)
            - guiding_material: Core waveguide material ("Si", "SiN")
            - lumapi_path: Path to Lumerical API installation
            - file_name: Base name for output files
            - mode_num: Number of modes to compute
            - mode_idx: Index of the injected mode
            - flag_extend: Whether to extend waveguides from ports
            - extension: Extension length in micrometers
            - flag_run_simulation: Whether to run the simulation
            - flag_boolean: Whether to apply boolean operations
            - solver_z_min/max: Simulation region z bounds
            - change_cladding: Whether to change top cladding to Si3N4

    Returns:
        Dictionary containing simulation results if flag_run_simulation is True,
        None otherwise
        
    Raises:
        FileNotFoundError: If GDS file or material files are not found
        ValueError: If parameters are invalid
        RuntimeError: If simulation fails
    """
    # Default settings
    p = dict(
        wavelength = 0.85,  # center wavelength (um)
        wav_span = 0.02,    # wavelength span (um)
        wav_step = 0.01,    # wavelength step (um)
        resolution = 6,     # spatial resolution, number of cells per wavelength
        temperature = 300,  # simulation temperature (K)
        predefined_gds = 'mmi_1x2_450_VISPIC2.gds', # default GDS file path
        material_type = "universal",    # material name
        guiding_material = 'SiN',       # core material
        lumapi_path = r"C:\Program Files\Lumerical\v251\api\python",        # Lumerical API path
        file_name = 'test_'+str(datetime.now().strftime('%Y%m%d%H%M%S')),   # output base name
        mode_num = 5,   # number of modes to compute
        mode_idx = 1,   # index of injected mode
        flag_extend = 1,    # extend waveguide?
        extension = 10,     # extension length (um)
        flag_run_simulation = 0,    # run simulation?
        flag_boolean = 0,           # apply boolean operation?
        solver_z_min = -1,          # simulation region z min (um)
        solver_z_max = 1,           # simulation region z max (um)
        change_cladding = False,    # True: replace top cladding with Si3N4
    )

    try:
        # Load user settings from config.json
        with open("config.json") as f:
            config = json.load(f)
        p.update(config)
    except FileNotFoundError:
        logger.warning("config.json not found, using default parameters")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config.json: {e}")
        raise ValueError(f"Invalid config.json format: {e}")

    # Update default setting with input parameters
    p.update(parameters)
    
    # Validate required parameters
    if not p.get('predefined_gds'):
        raise ValueError("GDS file path must be specified")
    
    # Validate file paths
    try:
        validate_file_path(p['predefined_gds'], "GDS")
    except FileNotFoundError as e:
        logger.error(f"GDS file validation failed: {e}")
        raise
    
    # Define the output GDS file name
    p['gds_file'] = p['file_name']+'.gds'

    # Convert parameters to local variables for backward compatibility
    for key, value in p.items():
        globals()[key] = value
        
    # Save parameters to a JSON file
    try:
        write_to_json(dict_name=p, json_name=file_name+'.json')
    except Exception as e:
        logger.error(f"Failed to save parameters: {e}")
        raise

    # Copy the predefined GDS to the output location
    try:
        device = gf.import_gds(predefined_gds, read_metadata=True)
        device.write_gds(gds_file, with_metadata=True)
        logger.info(f"GDS file copied to {gds_file}")
    except Exception as e:
        logger.error(f"Failed to import/copy GDS file: {e}")
        raise RuntimeError(f"GDS file processing failed: {e}")

    # Check if the simulation file already exists
    simulation_file = file_name+'_FDTD.fsp'
    if os.path.exists(simulation_file):
        logger.warning(f"Simulation file already exists: {simulation_file}")
        while True:
            try:
                response = input("Do you want to continue? (y/n): ").strip().lower()
                if response == 'y':
                    logger.info("Continuing with existing simulation file")
                    results = fdtd_from_gds(parameters=p)
                    return results
                elif response == 'n':
                    logger.info("Simulation cancelled by user")
                    return None
                else:
                    logger.info("Please enter 'y' or 'n'.")
            except KeyboardInterrupt:
                logger.info("Simulation cancelled by user")
                return None
    else:
        logger.info("Starting new simulation")
        results = fdtd_from_gds(parameters=p)
        return results

     

    