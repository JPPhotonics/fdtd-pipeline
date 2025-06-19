# Supplementary Code: Photonic Device Simulation with Lumerical and Tidy3D

This repository contains simulation scripts and utilities used in the publication:

**"Comparison of Lumerical FDTD and Tidy3D for three-dimensional FDTD simulations of passive silicon photonic components"**  
*Author(s): Zuyang Liu and Joyce K. S. Poon*  

---

## Overview

This code enables reproducible 3D FDTD simulations of silicon photonic devices using:

- **GDSFactory** for layout processing  
- **Lumerical FDTD** (desktop solver)  
- **Tidy3D** (cloud solver)  

Supported devices include directional couplers, waveguide crossings, MMIs, mode converters, and polarization splitter-rotators.

---

## Environment Setup

### Prerequisites

1. **Python 3.10** (recommended)
2. **Ansys Lumerical FDTD** (locally installed) - for desktop simulations
3. **Flexcompute Tidy3D** (with API access) - for cloud simulations

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd code_for_publication
   ```

2. **Create the conda environment:**
   ```bash
   conda env create -f environment.yml
   conda activate fdtd_sim
   ```

3. **Configure Tidy3D API key:**
   ```bash
   pip install pipx
   pipx run tidy3d configure --apikey=your_apikey_here
   ```
   
   Alternatively, download the config file from Tidy3D and save to `C:\Users\your_username\.tidy3d`

---

## Configuration

### Global Settings

Before running simulations, edit `config.json` to match your local environment:

```json
{
    "wavelength": 1.53,
    "wav_step": 0.005,
    "temperature": 300,
    "material_type": "universal",
    "guiding_material": "Si",
    "lumapi_path": "C:/Program Files/Lumerical/v251/api/python",
    "solver_z_min": -2,
    "solver_z_max": 2
}
```

> ⚠️ **Important:** Ensure `lumapi_path` correctly points to your Lumerical API installation directory.

### Device-Specific Settings

Each device script contains its own simulation parameters:
- **Resolution:** Number of cells per wavelength (default: 6)
- **Wavelength span:** Simulation bandwidth in nanometers (default: 20)
- **Mode index:** Injected mode number (Lumerical: 1-based, Tidy3D: 0-based)
- **Run simulation:** Boolean flag to execute simulation

---

## Running Simulations

### Available Devices

Each device has its own runnable script located at:
```
projects/FDTD_solvers/<device_name>/<device_name>.py
```

**Supported devices:**
- `coupler/` - Directional coupler
- `crossing/` - Waveguide crossing  
- `mmi2x2/` - 2×2 MMI coupler
- `mode_converter/` - Mode converter
- `polarization_splitter_rotator/` - Polarization splitter-rotator

### Example Usage

1. **Navigate to device directory:**
   ```bash
   cd projects/FDTD_solvers/coupler
   ```

2. **Edit simulation parameters in the script:**
   ```python
   # Select solver: 'lumerical' or 'tidy3d'
   solver = 'lumerical'
   
   # Simulation parameters
   res = 6           # resolution (cells per wavelength)
   span = 20         # wavelength span (nm)
   mode_idx = 0      # injected mode index
   flag_run_simulation = 1  # run simulation?
   ```

3. **Run the simulation:**
   ```bash
   python directional_coupler.py
   ```

### Output Files

Simulations generate the following output files:
- `*_fdtd.json` - Simulation parameters
- `*_FDTD.fsp` - Lumerical project file (Lumerical only)
- `*_results.hdf5` - Tidy3D results (Tidy3D only)
- `Data/` - Organized simulation results

---

## Code Structure

```
code_for_publication/
├── config.json                 # Global configuration
├── environment.yml             # Conda environment
├── gds_library/               # GDS files and PDK definitions
│   ├── cells_from_gds/        # Device GDS files
│   └── pdk_*.py              # PDK-specific functions
├── helper_functions/          # Core simulation utilities
│   ├── generic/              # Common utilities
│   ├── lumerical/            # Lumerical-specific functions
│   └── tidy3d/               # Tidy3D-specific functions
├── materials_library/         # Material property files
├── projects/                  # Device simulation scripts
│   └── FDTD_solvers/         # Individual device simulations
└── readme.md                 # This file
```

---

## Troubleshooting

### Common Issues

1. **Lumerical API not found:**
   - Verify `lumapi_path` in `config.json`
   - Check Lumerical installation directory
   - Ensure Python version compatibility

2. **Tidy3D authentication error:**
   - Verify API key configuration
   - Check internet connection
   - Ensure Tidy3D account has sufficient credits

3. **GDS file not found:**
   - Verify GDS file paths in device scripts
   - Check file permissions
   - Ensure GDS files are in correct format

### Logging

The code uses Python's logging module for detailed output. Log levels can be adjusted in `helper_functions/generic/misc.py`:

```python
logging.basicConfig(
    level=logging.INFO,  # Change to logging.DEBUG for more detail
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Contact

**Zuyang Liu**  
The Edward S. Rogers Sr. Department of Electrical and Computer Engineering  
University of Toronto  
📧 zuyang.liu@utoronto.ca

---

## License

This code is provided for peer review and academic reproducibility. Please cite the paper if you use or adapt this work.

---

## Version Information

- **Code Version:** 1.0.0
- **Last Updated:** 2025
- **Compatible with:** Python 3.10+, Lumerical FDTD v232+, Tidy3D v1.0+
