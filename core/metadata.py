import os
from PIL import Image
from PIL.ExifTags import TAGS

def analyze_metadata(file_path: str) -> dict:
    try:
        exif = None
        pillow_info = {}
        png_text = None
        software = None
        timestamps = []
        camera_info = {}
        comments = []
        total_metadata_size = 0
        unusual_fields = []
        assessment = 'Normal'
        assessment_reasons = []
        risk_contribution = 0
        
        try:
            with Image.open(file_path) as img:
                pillow_info = {k: str(v)[:100] for k, v in img.info.items() if k != 'exif'}
                
                if img.format == 'PNG':
                    png_text = {}
                    for k, v in img.info.items():
                        if isinstance(v, str):
                            png_text[k] = v[:100]
                            total_metadata_size += len(v)
                            
                raw_exif = img.getexif() if hasattr(img, 'getexif') else None
                if not raw_exif and hasattr(img, '_getexif'):
                    raw_exif = img._getexif()
                    
                if raw_exif:
                    exif = {}
                    for tag_id, data in raw_exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif[tag] = str(data)[:100]
                        total_metadata_size += len(str(data))
                        
                        if isinstance(tag, str):
                            tag_lower = tag.lower()
                            if 'software' in tag_lower or 'processing' in tag_lower:
                                software = str(data)
                            if 'date' in tag_lower or 'time' in tag_lower:
                                timestamps.append(f"{tag}: {data}")
                            if tag in ('Make', 'Model', 'LensModel'):
                                camera_info[tag] = str(data)
                            if 'comment' in tag_lower or 'description' in tag_lower:
                                comments.append(str(data))
                            
        except Exception:
            pass
            
        if total_metadata_size > 50000:
            assessment = 'Suspicious'
            assessment_reasons.append(f'Suspiciously large metadata ({total_metadata_size} bytes)')
            risk_contribution += 5
            
        if software and any(susp in software.lower() for susp in ['stego', 'hide', 'crypt', 'secret']):
            assessment = 'Suspicious'
            assessment_reasons.append(f'Suspicious software tag: {software}')
            risk_contribution += 8
            
        if not assessment_reasons:
            if total_metadata_size > 0:
                assessment = 'Normal'
            else:
                assessment = 'Normal'
                assessment_reasons.append('No significant metadata found')
                
        return {
            'exif': exif,
            'pillow_info': pillow_info,
            'png_text': png_text,
            'software': software,
            'timestamps': timestamps,
            'camera_info': camera_info if camera_info else None,
            'comments': comments,
            'total_metadata_size': total_metadata_size,
            'unusual_fields': unusual_fields,
            'assessment': assessment,
            'assessment_reasons': assessment_reasons,
            'risk_contribution': risk_contribution
        }
    except Exception as e:
        return {'error': str(e)}
