import os
import math

def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    counts = [0] * 256
    for byte in data:
        counts[byte] += 1
    for count in counts:
        if count > 0:
            p = count / length
            entropy -= p * math.log2(p)
    return entropy

def detect_trailing_data(file_path: str, image_format: str = None) -> dict:
    try:
        file_size = os.path.getsize(file_path)
        has_trailing_data = False
        image_end_offset = None
        trailing_bytes = 0
        trailing_data_preview = ""
        trailing_data_entropy = None
        assessment = "Normal"
        details = "No trailing data detected."
        risk_contribution = 0

        with open(file_path, 'rb') as f:
            data = f.read()

        if image_format == 'JPEG':
            idx = data.rfind(b'\xff\xd9')
            if idx != -1:
                image_end_offset = idx + 2
                
        elif image_format == 'PNG':
            idx = data.rfind(b'IEND')
            if idx != -1:
                image_end_offset = idx + 4 + 4
                if image_end_offset > file_size:
                    image_end_offset = file_size
                    
        elif image_format == 'BMP':
            if len(data) >= 6:
                declared_size = int.from_bytes(data[2:6], byteorder='little')
                if declared_size <= file_size and declared_size > 0:
                    image_end_offset = declared_size
                    
        elif image_format == 'GIF':
            idx = data.rfind(b'\x3b')
            if idx != -1:
                image_end_offset = idx + 1
                
        if image_end_offset is not None and image_end_offset < file_size:
            has_trailing_data = True
            trailing_bytes = file_size - image_end_offset
            t_data = data[image_end_offset:]
            trailing_data_preview = t_data[:64].hex()
            trailing_data_entropy = calculate_entropy(t_data)
            assessment = "WARNING: Data exists after expected image termination"
            details = f"Found {trailing_bytes} bytes of trailing data starting at offset {image_end_offset}."
            risk_contribution = 10

        return {
            'has_trailing_data': has_trailing_data,
            'image_end_offset': image_end_offset,
            'file_size': file_size,
            'trailing_bytes': trailing_bytes,
            'trailing_data_preview': trailing_data_preview,
            'trailing_data_entropy': trailing_data_entropy,
            'assessment': assessment,
            'details': details,
            'risk_contribution': risk_contribution
        }
        
    except Exception as e:
        return {'error': str(e)}
