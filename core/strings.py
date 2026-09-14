import os
import re
from typing import Dict, Any, List

# Core definitions for string analysis
SUSPICIOUS_KEYWORDS = [
    'powershell', 'cmd.exe', 'mshta', 'wscript', 'cscript', 
    'javascript', 'vbscript', 'base64', 'eval(', 'exec(', 
    'system(', 'shell', 'rundll32', 'regsvr32', 'certutil'
]

# Regex patterns (compiled as bytes since we read binary data)
URL_PATTERN = re.compile(rb'https?://[a-zA-Z0-9./\-_?&=]+')
IP_PATTERN = re.compile(rb'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
BASE64_PATTERN = re.compile(rb'(?:[A-Za-z0-9+/]{4}){12,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?')
ASCII_PRINTABLE = re.compile(rb'[\x20-\x7E]{4,}')

def analyze_strings(file_path: str, min_length: int = 4) -> Dict[str, Any]:
    """
    Extracts and analyzes strings from a file in a chunked, safe manner.
    Never executes or decodes contents.
    
    Args:
        file_path (str): Path to the file.
        min_length (int): Minimum length of strings to extract.
        
    Returns:
        dict: Structured string analysis results.
    """
    result = {
        'total_strings': 0,
        'ascii_strings': [],
        'urls': [],
        'ip_addresses': [],
        'domains': [],  # Currently not populated via separate regex, extracted from URLs if needed
        'suspicious_keywords': [],
        'long_base64_strings': [],
        'assessment': 'Clean',
        'assessment_reasons': [],
        'risk_contribution': 0,
        'note': 'String analysis identifies potential indicators; the presence of suspicious strings does not prove malicious intent.'
    }

    if not os.path.exists(file_path):
        result['assessment'] = 'Error'
        result['assessment_reasons'].append('File not found')
        return result

    chunk_size = 1024 * 1024  # 1MB chunks
    overlap = 1024  # Overlap to catch strings crossing boundaries

    try:
        all_ascii = []
        urls_set = set()
        ips_set = set()
        base64_set = set()
        suspicious_matches = []
        
        with open(file_path, 'rb') as f:
            buffer = b''
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                    
                data = buffer + chunk
                buffer = chunk[-overlap:] if len(chunk) >= overlap else chunk

                # Extract strings
                found_strings = ASCII_PRINTABLE.findall(data)
                
                for s_bytes in found_strings:
                    if len(s_bytes) < min_length:
                        continue
                    
                    try:
                        s = s_bytes.decode('ascii')
                        all_ascii.append(s)
                        
                        # Check keywords
                        s_lower = s.lower()
                        for kw in SUSPICIOUS_KEYWORDS:
                            if kw in s_lower:
                                if s not in suspicious_matches:
                                    suspicious_matches.append(s)
                    except UnicodeDecodeError:
                        pass
                
                # Extract URL, IPs, Base64
                urls_set.update(URL_PATTERN.findall(data))
                ips_set.update(IP_PATTERN.findall(data))
                base64_set.update(BASE64_PATTERN.findall(data))

        result['total_strings'] = len(all_ascii)
        
        # Deduplicate and decode the sets
        result['urls'] = list(set([u.decode('utf-8', errors='ignore') for u in urls_set]))[:100]
        result['ip_addresses'] = list(set([ip.decode('utf-8', errors='ignore') for ip in ips_set]))[:100]
        
        b64_list = [b.decode('utf-8', errors='ignore') for b in base64_set]
        result['long_base64_strings'] = [b for b in b64_list if len(b) > 50][:100]
        
        result['suspicious_keywords'] = list(set(suspicious_matches))[:100]
        result['ascii_strings'] = list(set(all_ascii))[:100]

        # Calculate Risk and Assessment
        risk = 0
        if result['suspicious_keywords']:
            risk += 15
            result['assessment_reasons'].append(f"Found {len(result['suspicious_keywords'])} suspicious keywords")
        
        if result['long_base64_strings']:
            risk += 10
            result['assessment_reasons'].append(f"Found {len(result['long_base64_strings'])} large base64-like strings")
            
        if result['urls'] or result['ip_addresses']:
            risk += 5
            result['assessment_reasons'].append(f"Found network indicators (URLs/IPs)")

        result['risk_contribution'] = min(risk, 40)
        
        if risk >= 15:
            result['assessment'] = 'Suspicious'
        elif risk > 0:
            result['assessment'] = 'Review'
            
    except Exception as e:
        result['assessment'] = 'Error'
        result['assessment_reasons'].append(f'Error reading file: {str(e)}')

    return result
