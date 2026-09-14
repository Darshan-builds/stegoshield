import os
import mimetypes
from PIL import Image

MAGIC_SIGNATURES = {
    b'\x89PNG\r\n\x1a\n': 'PNG',
    b'\xff\xd8\xff': 'JPEG',
    b'BM': 'BMP',
    b'GIF87a': 'GIF',
    b'GIF89a': 'GIF',
    b'RIFF': 'WebP' # Needs checking 8-11 for WEBP
}

def get_magic_format(data: bytes) -> str:
    for sig, fmt in MAGIC_SIGNATURES.items():
        if data.startswith(sig):
            if fmt == 'WebP':
                if len(data) >= 12 and data[8:12] == b'WEBP':
                    return 'WebP'
            else:
                return fmt
    return 'UNKNOWN'

def validate_format(file_path: str) -> dict:
    try:
        filename = os.path.basename(file_path)
        _, ext = os.path.splitext(filename)
        ext = ext.lower().replace('.', '')
        
        ext_map = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG', 'bmp': 'BMP', 'gif': 'GIF', 'webp': 'WebP'}
        declared_format = ext_map.get(ext, ext.upper())
        
        with open(file_path, 'rb') as f:
            header = f.read(16)
        
        detected_magic = get_magic_format(header)
        
        pillow_format = 'UNKNOWN'
        dimensions = None
        color_mode = None
        bit_depth = None
        try:
            with Image.open(file_path) as img:
                pillow_format = img.format or 'UNKNOWN'
                dimensions = img.size
                color_mode = img.mode
                if hasattr(img, 'bits'):
                    bit_depth = img.bits
                elif img.mode == 'RGB':
                    bit_depth = 24
                elif img.mode == 'RGBA':
                    bit_depth = 32
                elif img.mode == 'L':
                    bit_depth = 8
        except Exception:
            pass
            
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'unknown'
        
        mismatch = False
        mismatch_details = None
        risk_contribution = 0
        
        formats = [f for f in [declared_format, detected_magic, pillow_format] if f not in ('UNKNOWN', '')]
        if formats and len(set(formats)) > 1:
            mismatch = True
            mismatch_details = f"Extension claims {declared_format}, magic bytes show {detected_magic}, Pillow sees {pillow_format}"
            risk_contribution = 10
            assessment = 'SUSPICIOUS FORMAT MISMATCH'
        else:
            assessment = 'CONSISTENT'
            
        file_size = os.path.getsize(file_path)
            
        return {
            'filename': filename,
            'extension': ext,
            'declared_extension_format': declared_format,
            'detected_magic': detected_magic,
            'pillow_format': pillow_format,
            'mime_type': mime_type,
            'mismatch': mismatch,
            'mismatch_details': mismatch_details,
            'assessment': assessment,
            'file_size': file_size,
            'dimensions': dimensions,
            'color_mode': color_mode,
            'bit_depth': bit_depth,
            'risk_contribution': risk_contribution
        }
    except Exception as e:
        return {'error': str(e)}
