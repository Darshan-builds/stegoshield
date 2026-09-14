"""
StegoShield — Risk Scoring Engine

Computes an explainable risk score from analysis module findings.
Weights are configurable via config/scoring.json.
"""

import json
import os
from typing import Dict, Any, List


# Ordered severity levels from lowest to highest
SEVERITY_LEVELS = [
    {'name': 'LOW',      'max_score': 19,  'color': 'green',
     'action': 'File appears clean based on static heuristics. No immediate action required.'},
    {'name': 'GUARDED',  'max_score': 39,  'color': 'blue',
     'action': 'Minor anomalies detected. Recommend standard security review before use.'},
    {'name': 'REVIEW',   'max_score': 59,  'color': 'yellow',
     'action': 'Suspicious indicators found. Recommend analysis in an isolated environment.'},
    {'name': 'HIGH',     'max_score': 79,  'color': 'orange',
     'action': 'Multiple suspicious indicators. Do not execute. Preserve original and analyze in sandbox.'},
    {'name': 'CRITICAL', 'max_score': 100, 'color': 'red',
     'action': 'Critical indicators detected. Quarantine immediately. Conduct forensic analysis.'},
]

DEFAULT_WEIGHTS = {
    'format_mismatch': 15,
    'trailing_data': 20,
    'suspicious_structure': 15,
    'large_metadata': 10,
    'high_entropy': 10,
    'lsb_anomaly': 15,
    'embedded_executable': 25,
    'suspicious_strings': 10,
    'file_size_anomaly': 10,
    'metadata_anomaly': 10,
    'unusual_chunks': 15,
    'missing_metadata_all': 5,
}


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load risk scoring configuration from JSON file.
    
    Args:
        config_path: Path to scoring.json. Defaults to config/scoring.json
                     relative to the project root.
    
    Returns:
        Configuration dict with 'weights', 'severity_thresholds', 'max_score'.
    """
    if config_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'config', 'scoring.json')

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            return {
                'weights': cfg.get('weights', DEFAULT_WEIGHTS),
                'severity_thresholds': cfg.get('severity_thresholds', {}),
                'max_score': cfg.get('max_score', 100),
            }
        except Exception:
            pass

    return {
        'weights': dict(DEFAULT_WEIGHTS),
        'severity_thresholds': {
            'low': 19, 'guarded': 39, 'review': 59, 'high': 79, 'critical': 100
        },
        'max_score': 100,
    }


def _classify_severity(score: int, config: Dict) -> Dict[str, str]:
    """Classify a numeric score into a severity level."""
    thresholds = config.get('severity_thresholds', {})
    
    # Build ordered severity list from config or defaults
    levels = [
        ('LOW',      thresholds.get('low', 19),      'green'),
        ('GUARDED',  thresholds.get('guarded', 39),   'blue'),
        ('REVIEW',   thresholds.get('review', 59),    'yellow'),
        ('HIGH',     thresholds.get('high', 79),      'orange'),
        ('CRITICAL', thresholds.get('critical', 100),  'red'),
    ]
    
    for name, max_score, color in levels:
        if score <= max_score:
            # Find matching action from SEVERITY_LEVELS
            action = next(
                (s['action'] for s in SEVERITY_LEVELS if s['name'] == name),
                'Conduct further analysis.'
            )
            return {'name': name, 'color': color, 'action': action}
    
    return {'name': 'CRITICAL', 'color': 'red',
            'action': SEVERITY_LEVELS[-1]['action']}


def calculate_risk(findings: Dict[str, Any],
                   config_path: str = None) -> Dict[str, Any]:
    """
    Calculate an explainable risk score from analysis module findings.
    
    Each module's results are inspected for their risk_contribution field
    and/or specific indicators. The total is capped at max_score (100).
    
    Args:
        findings: Combined dict of all module results. Keys are module names
                  (e.g., 'format_validator', 'trailing_data', 'lsb_analyzer').
        config_path: Optional path to scoring.json override.
    
    Returns:
        Dict with score, severity, contributors list, explanation, and
        recommended_action. The score is fully reproducible from contributors.
    """
    config = load_config(config_path)
    weights = config.get('weights', DEFAULT_WEIGHTS)
    max_score = config.get('max_score', 100)
    
    score = 0
    contributors: List[Dict[str, Any]] = []
    
    def _add(indicator: str, points: int, description: str):
        nonlocal score
        if points > 0:
            # Cap individual contribution at its configured weight
            max_pts = weights.get(indicator, points)
            capped = min(points, max_pts)
            score += capped
            contributors.append({
                'indicator': indicator,
                'points': capped,
                'description': description,
            })
    
    # --- 1. Format Validation ---
    fmt = findings.get('format_validator', {})
    if fmt.get('mismatch', False):
        _add('format_mismatch', fmt.get('risk_contribution', 15),
             'File extension does not match detected format')
    
    # --- 2. Trailing Data ---
    trail = findings.get('trailing_data', {})
    if trail.get('has_trailing_data', False):
        pts = trail.get('risk_contribution', 0)
        if pts == 0:
            # Compute based on trailing bytes
            trailing_bytes = trail.get('trailing_bytes', 0)
            if trailing_bytes > 1000:
                pts = weights.get('trailing_data', 20)
            elif trailing_bytes > 0:
                pts = min(trailing_bytes // 50 + 5,
                         weights.get('trailing_data', 20))
        _add('trailing_data', pts,
             f"Data detected after image end marker ({trail.get('trailing_bytes', 0)} bytes)")
    
    # --- 3. Entropy ---
    ent = findings.get('entropy', {})
    overall_entropy = ent.get('overall_entropy', 0.0)
    if overall_entropy > 7.5:
        _add('high_entropy', weights.get('high_entropy', 10),
             f'Unusually high file entropy ({overall_entropy:.2f}/8.00)')
    elif overall_entropy > 7.2:
        _add('high_entropy', weights.get('high_entropy', 10) // 2,
             f'Elevated file entropy ({overall_entropy:.2f}/8.00)')
    
    # --- 4. LSB Analysis ---
    lsb = findings.get('lsb_analyzer', {})
    lsb_pts = lsb.get('risk_contribution', 0)
    if lsb_pts > 0:
        anomalous = lsb.get('anomalous_channels', [])
        desc = f"LSB statistical anomaly in channel(s): {', '.join(anomalous)}" if anomalous else "LSB statistical anomaly detected"
        _add('lsb_anomaly', lsb_pts, desc)
    
    # --- 5. Suspicious Strings ---
    strings = findings.get('strings', {})
    str_pts = strings.get('risk_contribution', 0)
    if str_pts > 0:
        reasons = strings.get('assessment_reasons', [])
        desc = f"Suspicious strings found: {'; '.join(reasons[:3])}" if reasons else "Suspicious string patterns detected"
        _add('suspicious_strings', str_pts, desc)
    
    # --- 6. Embedded Data ---
    embed = findings.get('embedded_data', {})
    embed_pts = embed.get('risk_contribution', 0)
    if embed_pts > 0:
        sigs = embed.get('signatures_found', [])
        types = [s.get('type', '?') for s in sigs[:3]]
        desc = f"Embedded signatures detected: {', '.join(types)}" if types else "Embedded data signatures found"
        _add('embedded_executable', embed_pts, desc)
    
    # --- 7. PNG/JPEG Structure ---
    for module_key, label in [('png_analyzer', 'PNG'), ('jpeg_analyzer', 'JPEG')]:
        struct = findings.get(module_key, {})
        struct_pts = struct.get('risk_contribution', 0)
        if struct_pts > 0:
            suspicious = struct.get('suspicious_chunks', struct.get('unusual_markers', []))
            desc = f"{label} structural anomalies detected"
            if suspicious:
                desc += f": {len(suspicious)} suspicious element(s)"
            _add('suspicious_structure', struct_pts, desc)
    
    # --- 8. Metadata ---
    meta = findings.get('metadata', {})
    meta_pts = meta.get('risk_contribution', 0)
    if meta_pts > 0:
        reasons = meta.get('assessment_reasons', [])
        desc = f"Metadata anomaly: {'; '.join(reasons[:2])}" if reasons else "Unusual metadata detected"
        _add('metadata_anomaly', meta_pts, desc)
    
    # --- Cap at max_score ---
    score = min(score, max_score)
    
    # --- Classify severity ---
    severity = _classify_severity(score, config)
    
    # --- Build explanation ---
    if not contributors:
        explanation = (
            f"The file received a risk score of {score}/100 (severity: {severity['name']}). "
            f"No significant suspicious indicators were detected by static analysis."
        )
    else:
        top_items = ', '.join(c['indicator'] for c in contributors[:3])
        explanation = (
            f"The file received a risk score of {score}/100 (severity: {severity['name']}). "
            f"Key contributing indicators: {top_items}. "
            f"This assessment is based on static heuristics and does NOT prove malware presence."
        )
    
    return {
        'score': score,
        'severity': severity['name'],
        'severity_color': severity['color'],
        'contributors': contributors,
        'total_indicators': len(contributors),
        'high_risk_indicators': sum(1 for c in contributors if c['points'] >= 15),
        'explanation': explanation,
        'recommended_action': severity['action'],
    }
