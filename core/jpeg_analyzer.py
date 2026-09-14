import os
import struct

JPEG_MARKERS = {
    'FFD8': 'SOI (Start of Image)',
    'FFE0': 'APP0 (JFIF)',
    'FFE1': 'APP1 (EXIF)',
    'FFE2': 'APP2 (ICC)',
    'FFE3': 'APP3',
    'FFE4': 'APP4',
    'FFE5': 'APP5',
    'FFE6': 'APP6',
    'FFE7': 'APP7',
    'FFE8': 'APP8',
    'FFE9': 'APP9',
    'FFEA': 'APP10',
    'FFEB': 'APP11',
    'FFEC': 'APP12 (Ducky)',
    'FFED': 'APP13 (Photoshop IRB)',
    'FFEE': 'APP14 (Adobe)',
    'FFEF': 'APP15',
    'FFDB': 'DQT (Define Quantization Table)',
    'FFC0': 'SOF0 (Start of Frame, Baseline DCT)',
    'FFC2': 'SOF2 (Start of Frame, Progressive DCT)',
    'FFC4': 'DHT (Define Huffman Table)',
    'FFDD': 'DRI (Define Restart Interval)',
    'FFDA': 'SOS (Start of Scan)',
    'FFFE': 'COM (Comment)',
    'FFD9': 'EOI (End of Image)'
}

def analyze_jpeg(file_path: str) -> dict:
    """
    Analyzes the structure and markers of a JPEG file.
    
    Args:
        file_path (str): The absolute path to the JPEG file.
        
    Returns:
        dict: A structured dictionary containing the analysis results.
    """
    result = {
        'is_jpeg': False,
        'markers': [],
        'total_markers': 0,
        'unusual_markers': [],
        'comments': [],
        'app_segments': [],
        'has_trailing_data': False,
        'trailing_bytes': 0,
        'assessment': 'Normal',
        'risk_contribution': 0
    }

    try:
        file_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as f:
            soi = f.read(2)
            if soi != b'\xff\xd8':
                result['assessment'] = 'Not a JPEG'
                return result
                
            result['is_jpeg'] = True
            
            # Record SOI
            result['markers'].append({
                'marker': 'FFD8',
                'name': 'SOI (Start of Image)',
                'offset': 0,
                'length': 2,
                'assessment': 'Normal',
                'details': None
            })
            result['total_markers'] += 1
            
            while True:
                marker_prefix = f.read(1)
                if not marker_prefix:
                    break
                    
                if marker_prefix != b'\xff':
                    continue
                    
                marker_code = f.read(1)
                if not marker_code or marker_code == b'\x00':
                    continue
                    
                marker_hex = f"FF{marker_code.hex().upper()}"
                marker_name = JPEG_MARKERS.get(marker_hex, 'Unknown Marker')
                offset = f.tell() - 2
                
                # Markers that don't have a length parameter following them
                standalone_markers = ['FFD8', 'FFD9', 'FF01'] + [f"FFD{i}" for i in range(8)]
                
                if marker_hex in standalone_markers:
                    result['markers'].append({
                        'marker': marker_hex,
                        'name': marker_name,
                        'offset': offset,
                        'length': 2,
                        'assessment': 'Normal',
                        'details': None
                    })
                    result['total_markers'] += 1
                    
                    if marker_hex == 'FFD9':
                        # Check for trailing data
                        current_pos = f.tell()
                        if current_pos < file_size:
                            result['has_trailing_data'] = True
                            result['trailing_bytes'] = file_size - current_pos
                        break
                    continue
                
                # Read length for segments with data
                length_bytes = f.read(2)
                if len(length_bytes) < 2:
                    break
                    
                segment_length = struct.unpack('>H', length_bytes)[0]
                
                assessment = 'Normal'
                details = []
                
                # Check for suspicious App segments (> 100KB)
                if marker_hex.startswith('FFE'):
                    result['app_segments'].append(marker_hex)
                    if segment_length > 100 * 1024:
                        assessment = 'Suspicious'
                        details.append(f"Unusually large APP segment: {segment_length} bytes")
                        result['unusual_markers'].append(marker_hex)
                        
                # Process COM segment
                elif marker_hex == 'FFFE':
                    try:
                        comment_data = f.read(segment_length - 2)
                        comment_text = comment_data.decode('utf-8', errors='ignore').strip()
                        result['comments'].append(comment_text)
                        
                        # Basic heuristics for suspicious comments
                        suspicious_keywords = ['<?php', '<script', 'eval(', 'base64']
                        if any(kw in comment_text.lower() for kw in suspicious_keywords):
                            assessment = 'Suspicious'
                            details.append("Suspicious content in comment")
                            result['unusual_markers'].append(marker_hex)
                        
                        # We already read the data, so we adjust offset manually
                        f.seek(offset + 2 + segment_length)
                    except Exception:
                        assessment = 'Review'
                        details.append("Error parsing comment segment")
                        f.seek(offset + 2 + segment_length)
                        
                # SOS (Start of Scan) - Need to scan forward for next marker (usually EOI)
                elif marker_hex == 'FFDA':
                    result['markers'].append({
                        'marker': marker_hex,
                        'name': marker_name,
                        'offset': offset,
                        'length': segment_length + 2,
                        'assessment': assessment,
                        'details': "; ".join(details) if details else None
                    })
                    result['total_markers'] += 1
                    
                    # Seek past SOS header
                    f.seek(segment_length - 2, os.SEEK_CUR)
                    
                    # Scan for next FF byte not followed by 00 (skip entropy-coded data)
                    chunk_size = 8192
                    found_next_marker = False
                    
                    while not found_next_marker:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        
                        # Look for FF D9 (EOI) or other markers
                        pos = 0
                        while pos < len(chunk) - 1:
                            if chunk[pos] == 0xFF and chunk[pos+1] != 0x00:
                                # We might have found a marker
                                marker = chunk[pos+1]
                                # If it's a restart marker, ignore
                                if 0xD0 <= marker <= 0xD7:
                                    pos += 2
                                    continue
                                
                                # Backtrack so the main loop picks it up
                                f.seek(f.tell() - len(chunk) + pos)
                                found_next_marker = True
                                break
                            pos += 1
                            
                    continue

                else:
                    # Seek past normal segment data
                    f.seek(segment_length - 2, os.SEEK_CUR)

                result['markers'].append({
                    'marker': marker_hex,
                    'name': marker_name,
                    'offset': offset,
                    'length': segment_length + 2,
                    'assessment': assessment,
                    'details': "; ".join(details) if details else None
                })
                result['total_markers'] += 1

            # Assess overall risk
            risk = 0
            if result['has_trailing_data']:
                risk += min(40, result['trailing_bytes'] // 100) # Capped at 40
            if result['unusual_markers']:
                risk += 25 * len(result['unusual_markers'])
                
            result['risk_contribution'] = min(risk, 100)
            
            if risk > 40:
                result['assessment'] = 'Suspicious'
            elif risk > 0:
                result['assessment'] = 'Review'

    except Exception as e:
        result['assessment'] = 'Error'
        result['details'] = f"Failed to parse JPEG structure: {str(e)}"
        
    return result
