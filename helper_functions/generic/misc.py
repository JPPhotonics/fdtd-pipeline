import os
import json
import numpy as np
import logging
from typing import Any, Dict, List, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComplexEncoder(json.JSONEncoder):
    """Custom JSON encoder for complex numbers and NumPy arrays.
    
    Handles serialization of complex numbers and NumPy arrays that are not
    natively supported by the standard JSON encoder.
    """
    def default(self, obj):
        if isinstance(obj, complex):
            return {"real": obj.real, "imag": obj.imag}
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

def convert_for_json(obj: Any) -> Any:
    """Recursively convert objects for JSON serialization.
    
    Converts:
        - NumPy arrays → lists
        - Items inside dicts and lists → recursively converted
    
    Args:
        obj: Object to convert for JSON serialization
        
    Returns:
        JSON-serializable object
    """
    if isinstance(obj, dict):
        return {k: convert_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_for_json(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, complex):
        return {"real": obj.real, "imag": obj.imag}
    return obj

def write_to_json(dict_name: Dict[str, Any], json_name: str) -> None:
    """Save a dictionary to a JSON file.
    
    Handles:
        - Nested dictionaries
        - NumPy arrays
        - Complex numbers
        - Automatic directory creation
    
    Args:
        dict_name: Dictionary to save
        json_name: Path to the output JSON file
    """
    try:
        converted_dict = convert_for_json(dict_name)
        
        # Create directories if they do not exist
        os.makedirs(os.path.dirname(json_name), exist_ok=True)
        
        with open(json_name, 'w') as f:
            json.dump(converted_dict, f, cls=ComplexEncoder, indent=2)
        
        logger.info(f"Parameters saved to {json_name}")
    except Exception as e:
        logger.error(f"Failed to save parameters to {json_name}: {e}")
        raise

def find_closest(lst: List[float], target: float) -> Tuple[float, int]:
    """Find the value and index of the item in a list closest to a given target.

    Args:
        lst: List of numeric values
        target: Target value to find closest match for

    Returns:
        Tuple containing (closest_value, index_of_closest_value)
    """
    if not lst:
        raise ValueError("Input list cannot be empty")
    
    lst = list(lst)
    closest_value = min(lst, key=lambda x: abs(x - target))
    closest_index = lst.index(closest_value)
    return closest_value, closest_index

def validate_file_path(file_path: str, file_type: str = "file") -> bool:
    """Validate that a file path exists and is accessible.
    
    Args:
        file_path: Path to the file to validate
        file_type: Type of file for error messages (e.g., "GDS", "material")
        
    Returns:
        True if file exists and is accessible
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_type} file not found: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read {file_type} file: {file_path}")
    return True

def ensure_directory_exists(directory_path: str) -> None:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory to ensure exists
    """
    os.makedirs(directory_path, exist_ok=True)
    logger.debug(f"Ensured directory exists: {directory_path}")