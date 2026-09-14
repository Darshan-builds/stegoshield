"""
StegoShield — Main Analysis Orchestrator

Runs all analysis modules in sequence, aggregates findings,
and computes the final risk assessment.
"""

import os
import datetime
import logging
import importlib
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)


def analyze_file(file_path: str,
                 config_path: str = None,
                 progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Main orchestrator for StegoShield analysis.
    
    Runs all applicable modules safely. Each module failure is isolated —
    one module error does not prevent other modules from executing.
    
    Args:
        file_path: Path to the file to analyze.
        config_path: Optional path to scoring.json override.
        progress_callback: Called between steps as callback(step_name, step_num, total).
    
    Returns:
        Complete analysis dict with 'findings', 'risk_assessment',
        'file_path', 'timestamp', and 'tool_version'.
    """
    analysis = {
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'tool_version': '1.0.0',
        'file_path': os.path.abspath(file_path) if os.path.exists(file_path) else file_path,
        'findings': {},
        'risk_assessment': {},
    }

    if not os.path.exists(file_path):
        analysis['error'] = 'File does not exist.'
        analysis['risk_assessment'] = {
            'score': 0, 'severity': 'UNKNOWN', 'severity_color': 'gray',
            'contributors': [], 'total_indicators': 0,
            'high_risk_indicators': 0, 'explanation': 'File not found.',
            'recommended_action': 'Verify the file path.',
        }
        return analysis

    def _progress(name, num, total):
        if progress_callback:
            try:
                progress_callback(name, num, total)
            except Exception:
                pass

    findings = analysis['findings']
    total_steps = 13  # 12 modules + risk engine

    # --- Step 1: Format Validation (run first to determine actual format) ---
    _progress('Format Validation', 1, total_steps)
    detected_format = None
    try:
        from core.format_validator import validate_format
        fmt_result = validate_format(file_path)
        findings['format_validator'] = fmt_result
        detected_format = (fmt_result.get('detected_magic') or
                          fmt_result.get('pillow_format') or '').upper()
    except Exception as e:
        logger.error(f"Format validation failed: {e}")
        findings['format_validator'] = {
            'error': str(e), 'assessment': 'Error', 'risk_contribution': 0
        }

    # --- Step 2: Cryptographic Hashing ---
    _progress('Cryptographic Hashing', 2, total_steps)
    try:
        from core.hashing import compute_hashes
        findings['hashing'] = compute_hashes(file_path)
    except Exception as e:
        logger.error(f"Hashing failed: {e}")
        findings['hashing'] = {'error': str(e)}

    # --- Step 3: Metadata Analysis ---
    _progress('Metadata Analysis', 3, total_steps)
    try:
        from core.metadata import analyze_metadata
        findings['metadata'] = analyze_metadata(file_path)
    except Exception as e:
        logger.error(f"Metadata analysis failed: {e}")
        findings['metadata'] = {
            'error': str(e), 'assessment': 'Error', 'risk_contribution': 0
        }

    # --- Step 4: Entropy Analysis ---
    _progress('Entropy Analysis', 4, total_steps)
    try:
        from core.entropy import analyze_file_entropy
        findings['entropy'] = analyze_file_entropy(file_path)
    except Exception as e:
        logger.error(f"Entropy analysis failed: {e}")
        findings['entropy'] = {
            'error': str(e), 'overall_entropy': 0.0, 'risk_contribution': 0
        }

    # --- Step 5: Trailing Data Detection ---
    _progress('Trailing Data Detection', 5, total_steps)
    try:
        from core.trailing_data import detect_trailing_data
        findings['trailing_data'] = detect_trailing_data(
            file_path, image_format=detected_format
        )
    except Exception as e:
        logger.error(f"Trailing data detection failed: {e}")
        findings['trailing_data'] = {
            'error': str(e), 'has_trailing_data': False, 'risk_contribution': 0
        }

    # --- Step 6: PNG Chunk Analysis (if PNG detected) ---
    _progress('PNG Analysis', 6, total_steps)
    if detected_format in ('PNG', None, ''):
        try:
            from core.png_analyzer import analyze_png
            png_result = analyze_png(file_path)
            if png_result.get('is_png', False):
                findings['png_analyzer'] = png_result
        except Exception as e:
            logger.error(f"PNG analysis failed: {e}")

    # --- Step 7: JPEG Structure Analysis (if JPEG detected) ---
    _progress('JPEG Analysis', 7, total_steps)
    if detected_format in ('JPEG', 'JPG', None, ''):
        try:
            from core.jpeg_analyzer import analyze_jpeg
            jpeg_result = analyze_jpeg(file_path)
            if jpeg_result.get('is_jpeg', False):
                findings['jpeg_analyzer'] = jpeg_result
        except Exception as e:
            logger.error(f"JPEG analysis failed: {e}")

    # --- Step 8: LSB Statistical Analysis ---
    _progress('LSB Analysis', 8, total_steps)
    try:
        from core.lsb_analyzer import analyze_lsb
        findings['lsb_analyzer'] = analyze_lsb(file_path)
    except Exception as e:
        logger.error(f"LSB analysis failed: {e}")
        findings['lsb_analyzer'] = {
            'error': str(e), 'analyzed': False, 'risk_contribution': 0
        }

    # --- Step 9: Noise / Randomness Analysis ---
    _progress('Noise Analysis', 9, total_steps)
    try:
        from core.noise_analyzer import analyze_noise
        findings['noise_analyzer'] = analyze_noise(file_path)
    except Exception as e:
        logger.error(f"Noise analysis failed: {e}")
        findings['noise_analyzer'] = {'error': str(e), 'analyzed': False}

    # --- Step 10: Suspicious String Analysis ---
    _progress('String Analysis', 10, total_steps)
    try:
        from core.strings import analyze_strings
        findings['strings'] = analyze_strings(file_path)
    except Exception as e:
        logger.error(f"String analysis failed: {e}")
        findings['strings'] = {
            'error': str(e), 'assessment': 'Error', 'risk_contribution': 0
        }

    # --- Step 11: Embedded Data Detection ---
    _progress('Embedded Data Detection', 11, total_steps)
    try:
        from core.embedded_data import detect_embedded_data
        findings['embedded_data'] = detect_embedded_data(file_path)
    except Exception as e:
        logger.error(f"Embedded data detection failed: {e}")
        findings['embedded_data'] = {
            'error': str(e), 'assessment': 'Clean', 'risk_contribution': 0
        }

    # --- Step 12: Risk Assessment ---
    _progress('Risk Assessment', 12, total_steps)
    try:
        from core.risk_engine import calculate_risk
        analysis['risk_assessment'] = calculate_risk(findings, config_path)
    except Exception as e:
        logger.error(f"Risk engine failed: {e}")
        analysis['risk_assessment'] = {
            'score': 0, 'severity': 'UNKNOWN', 'severity_color': 'gray',
            'contributors': [], 'total_indicators': 0,
            'high_risk_indicators': 0,
            'explanation': f'Risk calculation failed: {str(e)}',
            'recommended_action': 'Manual review recommended.',
        }

    _progress('Complete', 13, total_steps)
    return analysis
