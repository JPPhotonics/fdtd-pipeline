import json
import matplotlib.pyplot as plt

def read_nk(filename, material,
            wvl_key: str = 'lambda_mat',
            n_prefix: str = 'index_', k_prefix: str = 'extinction_',
            plot_on: bool = False):
    r""" read n, k vs. wavelength from a json file

    Args:
        filename (_type_): json file name, without '.json'.
        material (_type_): material name, e.g. SiN, SiO2, Si.
        wvl_key (str, optional): key in dictionary. Defaults to 'lambda_mat'.
        n_prefix (str, optional): key prefix in dictionary. Defaults to 'index_'.
        k_prefix (str, optional): key prefix in dictionary. Defaults to 'extinction_'.
        plot_on (bool, optional): flag to plot n, k vs. wvl. Defaults to false.

    Returns:
        result (dict): dictionary with wavelengths, n, k
    """
    
    with open(filename+'.json', 'r') as file:
        data = json.load(file)
    
    n_key = n_prefix + material
    k_key = k_prefix + material
    
    # create a new dictionary
    result = {}
    result['wvls'] = data[wvl_key]
    result['n'] = data[n_key]
    result['k'] = data[k_key]
    
    if plot_on:
        
        fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(6, 4))
        axs[0].plot(result['wvls'], result['n'], label='refractive index', color='b')
        axs[0].legend()
        axs[0].set_xlabel('wavelength')
        axs[1].plot(result['wvls'], result['k'], label='extinction ratio', color='r')
        axs[1].legend()
        axs[1].set_xlabel('wavelength')
        fig.suptitle(filename+', '+material)
        plt.tight_layout()
        plt.show()
        
    return result

def convert_txt_to_json(txt_file, json_file):

    r"""
    Converts a comma-delimited text file into a JSON file, where the keys are the column names from the first row of the text file, and the values are lists containing the numbers in each corresponding column.

    Parameters:
    input_file (str): The path to the input text file. The file should have a header row with column names, followed by rows of numerical data separated by commas.
    output_file (str): The path where the output JSON file will be saved.

    Returns:
    None. The function writes the converted data to the specified output JSON file.
    """

    with open(txt_file, 'r') as txt_file:
        lines = txt_file.readlines()
    
    column_names = lines[0].strip().split(',')
    data = {column_name: [] for column_name in column_names}

    for line in lines[1:]:
        values = line.strip().split(',')
        for i, value in enumerate(values):
            data[column_names[i]].append(float(value))

    with open(json_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)