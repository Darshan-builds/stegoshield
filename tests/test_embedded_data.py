import unittest
import tempfile
import os
from core.embedded_data import detect_embedded_data

class TestEmbeddedData(unittest.TestCase):
    def test_clean_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"A" * 200)
            filepath = f.name
        try:
            result = detect_embedded_data(filepath)
            self.assertEqual(result['total_indicators'], 0)
            self.assertEqual(len(result['signatures_found']), 0)
        finally:
            os.remove(filepath)

    def test_mz_signature_offset(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            # Write 150 bytes of garbage, then MZ signature
            f.write(b"A" * 150 + b"MZ" + b"\x00" * 50)
            filepath = f.name
        try:
            result = detect_embedded_data(filepath)
            self.assertGreaterEqual(result['total_indicators'], 1)
            # signatures_found is a list of dicts with 'type' key
            sig_types = [s.get('type', '') for s in result['signatures_found']]
            self.assertTrue(any("MZ" in t or "PE" in t for t in sig_types),
                          f"Expected MZ/PE in signatures, got: {sig_types}")
        finally:
            os.remove(filepath)
    
    def test_mz_at_offset_zero(self):
        """MZ at offset 0 should be skipped (it's the file's own header)."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"MZ" + b"\x00" * 200)
            filepath = f.name
        try:
            result = detect_embedded_data(filepath)
            # MZ at offset 0 should not be flagged as embedded
            sig_offsets = [s.get('offset', 0) for s in result['signatures_found']
                         if 'MZ' in s.get('type', '') or 'PE' in s.get('type', '')]
            self.assertTrue(all(o > 0 for o in sig_offsets) or len(sig_offsets) == 0)
        finally:
            os.remove(filepath)

if __name__ == "__main__":
    unittest.main()
