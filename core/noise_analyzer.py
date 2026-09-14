import numpy as np
from PIL import Image

def calculate_entropy(data):
    """Calculate the Shannon entropy of an array."""
    if len(data) == 0:
        return 0.0
    counts = np.bincount(data, minlength=256)
    probabilities = counts[counts > 0] / len(data)
    entropy = -np.sum(probabilities * np.log2(probabilities))
    return entropy

def analyze_noise(file_path: str) -> dict:
    """
    Analyzes image noise, randomness, and statistical properties.
    Generates histogram and LSB distribution data for UI rendering.
    
    Args:
        file_path (str): The absolute path to the image file.
        
    Returns:
        dict: Structured dictionary containing statistical analysis results.
    """
    result = {
        'analyzed': False,
        'channels': {},
        'overall_pixel_entropy': 0.0,
        'histogram_data': {
            'red': [],
            'green': [],
            'blue': [],
            'grayscale': []
        },
        'lsb_distribution': {
            'red': [],
            'green': [],
            'blue': []
        },
        'assessment': 'Normal',
        'details': ''
    }

    try:
        with Image.open(file_path) as img:
            # Generate grayscale for overall brightness analysis
            gray_img = img.convert('L')
            gray_array = np.array(gray_img).flatten()
            
            result['histogram_data']['grayscale'] = np.bincount(gray_array, minlength=256).tolist()
            result['overall_pixel_entropy'] = float(calculate_entropy(gray_array))

            if img.mode not in ('RGB', 'RGBA'):
                try:
                    img = img.convert('RGB')
                except Exception:
                    result['assessment'] = 'Limited Analysis'
                    result['details'] = 'Could not convert image to RGB for channel breakdown.'
                    result['analyzed'] = True
                    return result

            img_array = np.array(img)
            channel_names = ['red', 'green', 'blue']
            
            for i, channel_name in enumerate(channel_names):
                channel_data = img_array[:, :, i].flatten()
                
                # Statistical measures
                mean = float(np.mean(channel_data))
                var = float(np.var(channel_data))
                stddev = float(np.std(channel_data))
                entropy = float(calculate_entropy(channel_data))
                
                result['channels'][channel_name] = {
                    'mean': mean,
                    'variance': var,
                    'stddev': stddev,
                    'entropy': entropy
                }
                
                # Histogram data
                result['histogram_data'][channel_name] = np.bincount(channel_data, minlength=256).tolist()
                
                # LSB Distribution for visualization
                lsb_plane = channel_data & 1
                lsb_counts = np.bincount(lsb_plane, minlength=2)
                result['lsb_distribution'][channel_name] = lsb_counts.tolist()

            result['analyzed'] = True
            
            # Simple heuristic for noise assessment
            # High overall entropy (> 7.9) in images could imply heavy compression or noise/encryption
            if result['overall_pixel_entropy'] > 7.95:
                result['assessment'] = 'Review'
                result['details'] = 'Unusually high pixel entropy, suggesting heavy noise, encryption, or compression.'

    except Exception as e:
        result['assessment'] = 'Error'
        result['details'] = f"Failed to analyze image noise: {str(e)}"

    return result
