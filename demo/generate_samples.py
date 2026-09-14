import os
import io
from typing import Dict, Any, Optional
from PIL import Image
from PIL.PngImagePlugin import PngInfo

def _create_base_gradient() -> Image.Image:
    """
    Creates a base 400x300 gradient image (smooth blue-to-purple gradient).
    
    Returns:
        Image.Image: The generated Pillow Image object.
    """
    width, height = 400, 300
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    if pixels is None:
        raise ValueError("Failed to load image pixels.")
        
    for y in range(height):
        for x in range(width):
            # Blue to purple gradient
            r = int((x / width) * 100)
            g = 0
            b = int(155 + (y / height) * 100)
            pixels[x, y] = (r, g, b)
            
    return img

def generate_clean_image(output_path: str) -> str:
    """
    Generates a normal clean image with standard metadata.
    
    Args:
        output_path (str): The file path to save the image.
        
    Returns:
        str: The path to the generated image, or empty string on failure.
    """
    try:
        img = _create_base_gradient()
        metadata = PngInfo()
        metadata.add_text("Software", "StegoShield Demo Generator")
        metadata.add_text("Comment", "Clean test image")
        img.save(output_path, "PNG", pnginfo=metadata)
        return output_path
    except Exception as e:
        print(f"Error generating clean image: {e}")
        return ""

def generate_appended_data_image(output_path: str) -> str:
    """
    Generates an image with 500 bytes of harmless trailing text.
    
    Args:
        output_path (str): The file path to save the image.
        
    Returns:
        str: The path to the generated image, or empty string on failure.
    """
    try:
        img = _create_base_gradient()
        metadata = PngInfo()
        metadata.add_text("Software", "StegoShield Demo Generator")
        
        # Save to memory buffer first
        buffer = io.BytesIO()
        img.save(buffer, "PNG", pnginfo=metadata)
        png_data = buffer.getvalue()
        
        # Append 500 bytes of text
        base_text = b'STEGOSHIELD_DEMO_TRAILING_DATA: This is harmless demonstration content appended after the image end marker for testing purposes. '
        append_text = b''
        while len(append_text) < 500:
            append_text += base_text
        append_text = append_text[:500]
        
        with open(output_path, 'wb') as f:
            f.write(png_data)
            f.write(append_text)
            
        return output_path
    except Exception as e:
        print(f"Error generating appended data image: {e}")
        return ""

def generate_lsb_modified_image(output_path: str) -> str:
    """
    Generates an image with LSB modifications in the blue channel and trailing suspicious data.
    
    Args:
        output_path (str): The file path to save the image.
        
    Returns:
        str: The path to the generated image, or empty string on failure.
    """
    try:
        img = _create_base_gradient()
        pixels = img.load()
        
        if pixels is None:
            raise ValueError("Failed to load image pixels.")
            
        width, height = img.size
        
        import random
        # Use a deterministic pseudo-random sequence for LSB embedding
        # This simulates encrypted/compressed hidden data which produces
        # near-uniform bit distributions detectable by chi-square analysis
        rng = random.Random(42)  # Fixed seed for reproducibility
        total_pixels = width * height
        
        # Generate pseudo-random bits for the blue channel
        # This creates a near-perfect 50/50 LSB distribution
        random_bits = [rng.randint(0, 1) for _ in range(total_pixels)]
        
        # Embed random bits in the LSB of the blue channel for ALL pixels
        bit_idx = 0
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                # Clear LSB and set it to the random bit
                b = (b & 0xFE) | random_bits[bit_idx]
                pixels[x, y] = (r, g, b)
                bit_idx += 1
                
        buffer = io.BytesIO()
        metadata = PngInfo()
        metadata.add_text("Software", "StegoShield Demo Generator")
        img.save(buffer, "PNG", pnginfo=metadata)
        png_data = buffer.getvalue()
        
        # Add trailing bytes containing a suspicious string
        suspicious_string = b'demo_keyword: powershell http://example.test'
        padding = b'PADDING_' * 10
        trailing_data = padding + suspicious_string + padding
        
        with open(output_path, 'wb') as f:
            f.write(png_data)
            f.write(trailing_data)
            
        return output_path
    except Exception as e:
        print(f"Error generating LSB modified image: {e}")
        return ""

def generate_all_samples(output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates all 3 sample images.
    
    Args:
        output_dir (str, optional): The directory to save samples in. 
            Defaults to demo/samples/ relative to the project root.
            
    Returns:
        dict: A dictionary containing paths and descriptions for the generated samples.
    """
    if output_dir is None:
        # Resolve output_dir relative to the project root
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_file_dir)
        output_dir = os.path.join(project_root, 'demo', 'samples')
        
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(f"Failed to create output directory {output_dir}: {e}")
        return {}
    
    results = {}
    
    clean_path = os.path.join(output_dir, 'normal_clean.png')
    res_clean = generate_clean_image(clean_path)
    if res_clean:
        results['normal_clean'] = {
            'path': res_clean,
            'description': '400x300 gradient image with normal PNG metadata.',
            'expected_risk': 'LOW'
        }
    
    appended_path = os.path.join(output_dir, 'appended_data.png')
    res_appended = generate_appended_data_image(appended_path)
    if res_appended:
        results['appended_data'] = {
            'path': res_appended,
            'description': '400x300 gradient image with 500 bytes of harmless trailing text.',
            'expected_risk': 'GUARDED/REVIEW'
        }
    
    lsb_path = os.path.join(output_dir, 'lsb_modified.png')
    res_lsb = generate_lsb_modified_image(lsb_path)
    if res_lsb:
        results['lsb_modified'] = {
            'path': res_lsb,
            'description': '400x300 gradient image with LSB-embedded message in blue channel and trailing suspicious data.',
            'expected_risk': 'REVIEW/HIGH'
        }
    
    return results

if __name__ == '__main__':
    results = generate_all_samples()
    for name, info in results.items():
        print(f'{name}: {info["path"]}')
        print(f'  Description: {info["description"]}')
        print(f'  Expected risk: {info["expected_risk"]}')
