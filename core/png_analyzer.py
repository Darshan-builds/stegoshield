import struct
import os

PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
PNG_STANDARD_CHUNKS = {'IHDR', 'PLTE', 'IDAT', 'IEND', 'cHRM', 'gAMA', 'iCCP', 'sBIT', 'sRGB', 'bKGD', 'hIST', 'tRNS', 'pHYs', 'sPLT', 'tIME', 'iTXt', 'tEXt', 'zTXt', 'eXIf'}
PNG_CRITICAL_CHUNKS = {'IHDR', 'PLTE', 'IDAT', 'IEND'}

def analyze_png(file_path: str) -> dict:
    """
    Analyzes the chunks and structure of a PNG file.
    
    Args:
        file_path (str): The absolute path to the PNG file.
        
    Returns:
        dict: A structured dictionary containing the analysis results.
    """
    result = {
        'is_png': False,
        'chunks': [],
        'total_chunks': 0,
        'unknown_chunks': [],
        'suspicious_chunks': [],
        'ordering_issues': [],
        'assessment': 'Normal',
        'risk_contribution': 0
    }

    try:
        with open(file_path, 'rb') as f:
            signature = f.read(8)
            if signature != PNG_SIGNATURE:
                result['assessment'] = 'Not a PNG'
                return result
            
            result['is_png'] = True
            
            file_size = os.path.getsize(file_path)
            
            chunk_index = 0
            has_ihdr = False
            has_iend = False
            text_chunk_count = 0
            
            while True:
                length_bytes = f.read(4)
                if not length_bytes:
                    break
                if len(length_bytes) < 4:
                    result['suspicious_chunks'].append("Unexpected EOF reading chunk length")
                    break
                    
                chunk_length = struct.unpack('>I', length_bytes)[0]
                chunk_type_bytes = f.read(4)
                
                if len(chunk_type_bytes) < 4:
                    result['suspicious_chunks'].append("Unexpected EOF reading chunk type")
                    break
                    
                try:
                    chunk_type = chunk_type_bytes.decode('ascii')
                except UnicodeDecodeError:
                    chunk_type = f"HEX:{chunk_type_bytes.hex()}"
                    
                offset = f.tell() - 8
                
                category = 'Standard' if chunk_type in PNG_STANDARD_CHUNKS else 'Unknown/Private'
                assessment = 'Normal'
                details = []
                
                # Check for Suspicious Length (> 1MB)
                if chunk_length > 1024 * 1024:
                    assessment = 'Suspicious'
                    details.append(f"Excessive chunk size: {chunk_length} bytes")
                    result['suspicious_chunks'].append(chunk_type)
                    
                # Check Unknown chunks
                if category == 'Unknown/Private':
                    assessment = 'Review'
                    details.append("Non-standard chunk type")
                    result['unknown_chunks'].append(chunk_type)
                    
                # Track Metadata chunks
                if chunk_type in {'tEXt', 'zTXt', 'iTXt'}:
                    category = 'Metadata'
                    text_chunk_count += 1
                    
                # Ordering checks
                if chunk_index == 0 and chunk_type != 'IHDR':
                    result['ordering_issues'].append(f"First chunk is {chunk_type}, expected IHDR")
                if chunk_type == 'IHDR':
                    has_ihdr = True
                if chunk_type == 'IEND':
                    has_iend = True
                    if f.tell() + chunk_length + 4 < file_size:
                        result['suspicious_chunks'].append("Trailing data found after IEND")
                        
                if has_iend and chunk_type != 'IEND':
                    result['ordering_issues'].append(f"Chunk {chunk_type} found after IEND")
                
                chunk_info = {
                    'type': chunk_type,
                    'length': chunk_length,
                    'offset': offset,
                    'category': category,
                    'assessment': assessment,
                    'details': "; ".join(details) if details else None
                }
                
                result['chunks'].append(chunk_info)
                result['total_chunks'] += 1
                chunk_index += 1
                
                # Seek past chunk data and CRC (buffered skip)
                try:
                    f.seek(chunk_length + 4, os.SEEK_CUR)
                except Exception:
                    result['suspicious_chunks'].append("Malformed file structure: Cannot seek past chunk")
                    break

            if text_chunk_count > 10:
                result['suspicious_chunks'].append(f"Excessive text chunks found ({text_chunk_count})")
                
            if not has_ihdr:
                result['ordering_issues'].append("Missing IHDR chunk")
            if not has_iend:
                result['ordering_issues'].append("Missing IEND chunk")
                
            # Aggregate risk
            risk = 0
            if result['suspicious_chunks']:
                risk += 20 * len(result['suspicious_chunks'])
            if result['unknown_chunks']:
                risk += 5 * len(result['unknown_chunks'])
            if result['ordering_issues']:
                risk += 15 * len(result['ordering_issues'])
                
            result['risk_contribution'] = min(risk, 100)
            if risk > 40:
                result['assessment'] = 'Suspicious'
            elif risk > 0:
                result['assessment'] = 'Review'
            
    except Exception as e:
        result['suspicious_chunks'].append(f"Analysis error: {str(e)}")
        result['assessment'] = 'Error'
        
    return result
