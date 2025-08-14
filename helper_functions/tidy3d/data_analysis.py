# Zuyang Liu (2023)
import tidy3d as td
import numpy as np
import matplotlib.pyplot as plt
import logging
from typing import Tuple, Optional, Dict, Any, Union
from pathlib import Path

logger = logging.getLogger(__name__)

def read_mode_monitor_from_file(
    fname: str | None = None,
    monitor: str | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Read mode monitor data from a Tidy3D simulation file.
    
    Args:
        fname: Path to the simulation data file (.hdf5)
        monitor: Name of the mode monitor to extract data from
        
    Returns:
        Tuple of (wavelengths, mode_coefficients) where:
            - wavelengths: Array of wavelengths in micrometers
            - mode_coefficients: Array of mode power coefficients (normalized)
            
    Raises:
        FileNotFoundError: If simulation file is not found
        KeyError: If monitor name is not found in simulation data
        ValueError: If monitor data is invalid
    """
    if fname is None:
        raise ValueError("File name must be specified")
    if monitor is None:
        raise ValueError("Monitor name must be specified")
        
    try:
        sim_data = td.SimulationData.from_file(fname)
        mode_data = sim_data[monitor]
        coeffs = np.abs(mode_data.amps.sel(direction="+"))**2
        lambdas = td.C_0 / mode_data.amps.f
        
        logger.info(f"Successfully read mode data from {fname}, monitor: {monitor}")
        logger.info(f"Wavelength range: {lambdas.min():.3f} - {lambdas.max():.3f} μm")
        logger.info(f"Number of modes: {coeffs.shape[1] if len(coeffs.shape) > 1 else 1}")
        
        return lambdas, coeffs
        
    except FileNotFoundError:
        logger.error(f"Simulation file not found: {fname}")
        raise
    except KeyError as e:
        logger.error(f"Monitor '{monitor}' not found in simulation data. Available monitors: {list(sim_data.keys())}")
        raise
    except Exception as e:
        logger.error(f"Error reading mode data: {e}")
        raise ValueError(f"Failed to read mode data: {e}")