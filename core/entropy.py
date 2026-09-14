import math
import os

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

def analyze_file_entropy(file_path: str) -> dict:
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            
        file_size = len(data)
        overall_entropy = calculate_entropy(data)
        
        if overall_entropy >= 7.5:
            interpretation = 'Very High'
            warning_level = 'high'
        elif overall_entropy >= 7.0:
            interpretation = 'High'
            warning_level = 'elevated'
        elif overall_entropy >= 5.0:
            interpretation = 'Moderate'
            warning_level = 'normal'
        else:
            interpretation = 'Low'
            warning_level = 'normal'
            
        regions = []
        if file_size > 0:
            first_chunk = data[:1024]
            regions.append({'name': 'first_1024', 'entropy': calculate_entropy(first_chunk), 'offset': 0, 'size': len(first_chunk)})
            
            if file_size > 2048:
                mid_offset = (file_size // 2) - 512
                mid_chunk = data[mid_offset:mid_offset+1024]
                regions.append({'name': 'middle_1024', 'entropy': calculate_entropy(mid_chunk), 'offset': mid_offset, 'size': len(mid_chunk)})
                
            if file_size > 1024:
                last_offset = max(1024, file_size - 1024)
                last_chunk = data[last_offset:]
                regions.append({'name': 'last_1024', 'entropy': calculate_entropy(last_chunk), 'offset': last_offset, 'size': len(last_chunk)})
                
        return {
            'overall_entropy': overall_entropy,
            'max_entropy': 8.0,
            'normalized': overall_entropy / 8.0,
            'interpretation': interpretation,
            'warning_level': warning_level,
            'regions': regions,
            'note': 'High entropy can be associated with compressed, encrypted, packed, or otherwise high-randomness data and is therefore only one indicator.'
        }
    except Exception as e:
        return {'error': str(e)}
