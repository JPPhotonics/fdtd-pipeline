from helper_functions.generic.materials import read_nk
import numpy as np

c = 299792458 # speed of light in vacuum, m/s

def add_material_sampled3d(
        project, 
        file, 
        display_name, 
        color: list = [0, 0, 1, 0]
        ):
    r"""Add a sampled 3D material to the Lumerical project using n/k data.

    Args:
        project: Lumerical project object
        file (str): Path to the file containing n/k data
        display_name (str): Display name for the material in Lumerical
        color (list): RGBA color for material visualization in GUI
    """
    # read wavelength and refractive index data from file
    temp = read_nk(
        filename=file, 
        material='', 
        wvl_key='wavelength(m)', 
        n_prefix='Re(index)', 
        k_prefix='Im(index)'
        )
    # create new material
    new_mat = project.addmaterial('Sampled 3D data')

    # convert wavelength to frequency
    f = c/np.array(temp['wvls'])

    # calculate permittivity (ε = n^2 for non-magnetic materials)
    eps = np.array(temp['n'])**2
    
    # combine frequency and permittivity into 2D array
    data = np.column_stack((f, eps))
    
    # assign data and properties to the new material
    project.setmaterial(new_mat, 'Name', display_name)
    project.setmaterial(display_name, 'sampled data', data)
    project.setmaterial(display_name, 'color', np.array(color))
    project.setmaterial(display_name, 'tolerance', 0.001)