import os
import sys
import numpy as np
import tidy3d as td
from tidy3d.plugins.dispersion import FastDispersionFitter, AdvancedFastFitterParam
import matplotlib.pyplot as plt
import json
import logging
from typing import Tuple, Optional

from tidy3d.plugins.dispersion import AdvancedFitterParam
from tidy3d.plugins.dispersion.web import run as run_fitter

logger = logging.getLogger(__name__)

def fit_pole_residue_material(filename: str,
                              output_file: str,
                              n_name: str,
                              k_name: str,
                              material_name: str,
                              wav_range: Tuple[float, float] = (0.4, 2.0),
                              web_service: bool = False) -> None:
    """Perform dispersion fitting on n, k data and save fitting result to a JSON file.
    
    Args:
        filename: Path to the material data file
        output_file: Path to save the fitted material data
        n_name: Name of the real refractive index column in the data
        k_name: Name of the imaginary refractive index column in the data
        material_name: Name of the material
        wav_range: Wavelength range for fitting (min, max) in micrometers
        web_service: Whether to use web service for fitting
        
    Raises:
        FileNotFoundError: If input file is not found
        ValueError: If fitting fails
    """
    
    try:
        # Read n, k data from file
        with open(filename) as f:
            mat = json.load(f)
        wvl_um = np.array(mat['wavelength(m)'])*1e6
        n_data = np.array(mat[n_name])
        k_data = np.array(mat[k_name])
        
        # Pole residue fitting
        fitter = FastDispersionFitter(wvl_um=wvl_um,
                                      n_data=n_data,
                                      k_data=k_data,
                                      wvl_range=wav_range,)
        
        if web_service:
            logger.info('Starting web service fitting')
            medium, rms_error = run_fitter(
                fitter,
                num_poles=6, tolerance_rms=1e-5, num_tries=50, 
                advanced_param = AdvancedFitterParam(nlopt_maxeval=5000),
            )
        else:
            advanced_param = AdvancedFastFitterParam(weights=(1,1))
            logger.info('Starting local fitting')

            medium, rms_error = fitter.fit(
                max_num_poles=1, 
                advanced_param=advanced_param, 
                tolerance_rms=2e-2
            )

        logger.info(f"RMS error: {rms_error:.6f}")    

        fitter.plot(medium)
        plt.xlabel('wavelength (um)')
        plt.show()
        
        medium.to_file(output_file)
        logger.info(f"Fitted material saved to {output_file}")
        
    except FileNotFoundError:
        logger.error(f"Material data file not found: {filename}")
        raise
    except Exception as e:
        logger.error(f"Fitting failed: {e}")
        raise ValueError(f"Material fitting failed: {e}")
    
def load_pole_material(filename: str) -> td.PoleResidue:
    """Load pole residue data to Tidy3D as a new medium.
    
    Args:
        filename: Path to the pole residue material file (without .json extension)
        
    Returns:
        Tidy3D PoleResidue medium object
        
    Raises:
        FileNotFoundError: If material file is not found
    """
    try:
        medium = td.PoleResidue.from_file(filename+'.json')
        logger.info(f"Pole material loaded from {filename}.json")
        return medium
    except FileNotFoundError:
        logger.error(f"Pole material file not found: {filename}.json")
        raise
    except Exception as e:
        logger.error(f"Failed to load pole material from {filename}: {e}")
        raise

if __name__ == "__main__":
    
    current_directory = os.getcwd()
    sys.path.append(current_directory)
    
    # filename = r'materials_library\VisPDK_materials_mid_SiN.json'
    filename = r'materials_library\universal_SiN - Copy.json'
    n_name = 'Re(index)'
    k_name = 'Im(index)'
    material_name = 'SiN'
    output_file = r'materials_library\test.json'
    
    fit_pole_residue_material(
        filename=filename, 
        n_name=n_name, k_name=k_name, 
        material_name=material_name, 
        output_file=output_file,
        wav_range=(0.7, 1.5),
        web_service=False,
        )