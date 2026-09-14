"""
StegoShield — LSB Statistical Analysis Module

Performs defensive Least Significant Bit analysis to identify potential
steganographic anomalies. Statistical indicators do NOT prove hidden data.
"""

import math
import numpy as np
from PIL import Image
from scipy.stats import chisquare
from typing import Dict, Any


def _lsb_entropy(bits: np.ndarray) -> float:
    """Calculate Shannon entropy of a binary (0/1) array. Max = 1.0 bit."""
    if len(bits) == 0:
        return 0.0
    counts = np.bincount(bits, minlength=2)
    probs = counts / len(bits)
    # Filter out zero probabilities
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log2(probs)))


def _chi_square_pairs(lsb_plane: np.ndarray) -> tuple:
    """
    Chi-square test on sequential LSB bit-pair frequencies.
    
    In a natural image, adjacent pixel LSBs follow patterns dictated by
    image content. Steganographic embedding (especially LSB replacement)
    tends to make pairs approach a uniform distribution.
    
    Returns (chi_stat, p_value).
    """
    total = len(lsb_plane)
    if total < 4:
        return 0.0, 1.0
    
    num_pairs = total // 2
    pairs = (lsb_plane[0:num_pairs * 2:2] << 1) | lsb_plane[1:num_pairs * 2:2]
    pair_counts = np.bincount(pairs, minlength=4).astype(float)
    
    expected = np.full(4, num_pairs / 4.0)
    if np.any(expected == 0):
        return 0.0, 1.0
    
    chi_stat, p_val = chisquare(pair_counts, f_exp=expected)
    return float(chi_stat), float(p_val)


def _chi_square_bytes(channel_data: np.ndarray) -> tuple:
    """
    Chi-square test on byte-level PoV (Pairs of Values) for LSB detection.
    
    Compares observed frequencies of (2k, 2k+1) value pairs to detect
    LSB replacement steganography. This is more robust than simple
    bit counting for natural images.
    
    Returns (chi_stat, p_value).
    """
    total = len(channel_data)
    if total < 10:
        return 0.0, 1.0
    
    # Count occurrences of each byte value
    hist = np.bincount(channel_data, minlength=256).astype(float)
    
    # For LSB replacement detection: compare adjacent value pairs
    # e.g., count(0) vs count(1), count(2) vs count(3), etc.
    # In an unmodified image, these pairs follow natural patterns.
    # After LSB embedding, pairs (2k) and (2k+1) tend to equalize.
    r_values = []
    for k in range(128):
        v0 = hist[2 * k]
        v1 = hist[2 * k + 1]
        pair_sum = v0 + v1
        if pair_sum > 4:  # Only consider pairs with enough samples
            expected = pair_sum / 2.0
            r_values.append((v0 - expected) ** 2 / expected +
                          (v1 - expected) ** 2 / expected)
    
    if not r_values:
        return 0.0, 1.0
    
    # Sum the chi-square contributions
    chi_stat = sum(r_values)
    # Degrees of freedom = number of pairs tested
    df = len(r_values)
    
    # Use scipy for p-value from chi-square distribution
    from scipy.stats import chi2
    p_val = 1.0 - chi2.cdf(chi_stat, df)
    
    return float(chi_stat), float(p_val)


def analyze_lsb(file_path: str) -> Dict[str, Any]:
    """
    Performs defensive LSB statistical analysis on an image file.
    
    Analyzes per-channel LSB distribution, entropy, and chi-square
    statistics to identify potential steganographic modifications.
    
    Args:
        file_path: Path to the image file to analyze.
        
    Returns:
        Structured dict with LSB analysis results per channel,
        overall assessment, and risk contribution (0-15).
    """
    result = {
        'analyzed': False,
        'image_mode': 'Unknown',
        'channels': {},
        'overall_lsb_assessment': 'Normal',
        'anomalous_channels': [],
        'chi_square_note': '',
        'assessment': 'Normal',
        'risk_contribution': 0,
        'note': ('Potential steganographic anomaly indicators do not '
                 'prove the presence of hidden data.')
    }

    try:
        with Image.open(file_path) as img:
            result['image_mode'] = img.mode

            # Convert to RGB for consistent analysis
            if img.mode not in ('RGB', 'RGBA'):
                try:
                    img = img.convert('RGB')
                except Exception:
                    result['assessment'] = 'Skipped'
                    result['chi_square_note'] = (
                        'Unsupported color mode for LSB extraction.')
                    return result

            # Subsample large images for performance (max ~1M pixels)
            width, height = img.size
            if width * height > 1_000_000:
                scale = math.sqrt(1_000_000 / (width * height))
                new_size = (max(1, int(width * scale)),
                           max(1, int(height * scale)))
                img = img.resize(new_size, Image.Resampling.NEAREST)

            img_array = np.array(img)
            
            # Handle different channel counts
            if len(img_array.shape) < 3:
                # Grayscale - add channel dimension
                img_array = img_array[:, :, np.newaxis]
            
            num_channels = min(img_array.shape[2], 3)  # Analyze RGB only
            channel_names = ['red', 'green', 'blue'][:num_channels]
            
            anomaly_score = 0
            channels_analyzed = 0

            for i, ch_name in enumerate(channel_names):
                channel_data = img_array[:, :, i].flatten()
                total_pixels = len(channel_data)
                
                if total_pixels == 0:
                    continue
                
                channels_analyzed += 1
                
                # Extract LSB plane
                lsb_plane = (channel_data & 1).astype(np.int32)

                # Count 0s and 1s
                counts = np.bincount(lsb_plane, minlength=2)
                pct_0 = float(counts[0] / total_pixels)
                pct_1 = float(counts[1] / total_pixels)

                # LSB entropy (max 1.0 for binary)
                entropy = _lsb_entropy(lsb_plane)

                # Chi-square on bit pairs
                pair_chi, pair_p = _chi_square_pairs(lsb_plane)
                
                # Chi-square on byte-level PoV (more robust)
                byte_chi, byte_p = _chi_square_bytes(channel_data)

                # Assessment logic:
                # Natural images have structured LSB patterns due to smooth
                # gradients, edges, etc. Their chi-square byte PoV test 
                # typically shows LOW p-values (structured, non-uniform pairs).
                #
                # LSB steganography makes value-pairs equalize, leading to
                # HIGH p-values in the byte PoV test.
                #
                # We flag a channel as anomalous ONLY if:
                # - The byte-level PoV p-value is high (> 0.10), suggesting
                #   value pairs have been equalized by LSB replacement, AND
                # - The LSB distribution is close to 50/50 (entropy > 0.95)
                
                ch_assessment = 'Normal'
                ch_anomaly = False
                
                # Primary indicator: byte-level PoV chi-square
                if byte_p > 0.10 and entropy > 0.95:
                    # High p-value means pairs are suspiciously equalized
                    ch_assessment = 'Anomalous'
                    ch_anomaly = True
                elif byte_p > 0.05 and entropy > 0.98:
                    ch_assessment = 'Slightly Anomalous'
                    ch_anomaly = True
                
                if ch_anomaly:
                    result['anomalous_channels'].append(ch_name)
                    anomaly_score += 1

                result['channels'][ch_name] = {
                    'lsb_zero_pct': round(pct_0, 4),
                    'lsb_one_pct': round(pct_1, 4),
                    'lsb_entropy': round(entropy, 6),
                    'chi_square_statistic': round(byte_chi, 2),
                    'chi_square_p_value': round(byte_p, 6),
                    'assessment': ch_assessment
                }

            result['analyzed'] = True

            # --- Inter-channel LSB comparison ---
            # Steganographic LSB embedding typically targets a single channel,
            # creating a detectable difference in LSB statistics between channels.
            # We compare the LSB zero/one balance across channels.
            if channels_analyzed >= 3 and anomaly_score == 0:
                ch_stats = []
                for ch_name in channel_names:
                    ch_data = result['channels'].get(ch_name, {})
                    # Use the deviation from 50/50 as the measure
                    pct_0 = ch_data.get('lsb_zero_pct', 0.5)
                    deviation = abs(pct_0 - 0.5)
                    ent = ch_data.get('lsb_entropy', 0.0)
                    ch_stats.append((ch_name, deviation, ent))
                
                if len(ch_stats) >= 3:
                    # Sort by deviation — channel closest to 50/50 first
                    ch_stats.sort(key=lambda x: x[1])
                    
                    # Check for a single channel that differs significantly
                    # from the other two. Compare the channel with the
                    # smallest deviation to the one with the largest.
                    # If one channel is very close to 50/50 (deviation < 0.02)
                    # while another is far (deviation > 0.10), the close one
                    # may have been modified.
                    closest_name, closest_dev, closest_ent = ch_stats[0]
                    middle_name, middle_dev, middle_ent = ch_stats[1]
                    farthest_name, farthest_dev, farthest_ent = ch_stats[2]
                    
                    # Only flag if the closest-to-50/50 channel is
                    # significantly closer than the other two
                    # AND the other two are consistent with each other
                    if (closest_dev < 0.02 and closest_ent > 0.98 and
                        middle_dev > 0.08 and farthest_dev > 0.08):
                        # One channel suspiciously close to perfect 50/50
                        result['channels'][closest_name]['assessment'] = 'Anomalous'
                        result['anomalous_channels'].append(closest_name)
                        anomaly_score += 1
                        result['chi_square_note'] = (
                            f'Channel {closest_name} shows near-perfect 50/50 '
                            f'LSB distribution ({closest_dev:.4f} deviation) '
                            f'while other channels show natural variation '
                            f'({middle_name}: {middle_dev:.4f}, '
                            f'{farthest_name}: {farthest_dev:.4f}). '
                            f'This pattern is consistent with selective '
                            f'LSB steganographic modification.'
                        )


            # Overall assessment and risk contribution (max 15 per config)
            if anomaly_score >= 2:
                result['overall_lsb_assessment'] = 'Anomalous'
                result['assessment'] = 'Suspicious'
                result['risk_contribution'] = 15
            elif anomaly_score == 1:
                result['overall_lsb_assessment'] = 'Slightly Anomalous'
                result['assessment'] = 'Review'
                result['risk_contribution'] = 8
            else:
                result['overall_lsb_assessment'] = 'Normal'
                result['assessment'] = 'Normal'
                result['risk_contribution'] = 0

    except FileNotFoundError:
        result['assessment'] = 'Error'
        result['chi_square_note'] = 'File not found.'
    except Exception as e:
        result['assessment'] = 'Error'
        result['chi_square_note'] = f'Failed to analyze LSB: {str(e)}'

    return result

