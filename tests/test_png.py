import unittest
import tempfile
import os
from PIL import Image
from core.png_analyzer import analyze_png

class TestPngAnalyzer(unittest.TestCase):
    def test_analyze_valid_png(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            filepath = f.name
        try:
            img = Image.new("RGB", (10, 10), color="blue")
            img.save(filepath, "PNG")
            
            result = analyze_png(filepath)
            self.assertEqual(result['is_png'], True)
            self.assertIn('chunks', result)
            self.assertIn('total_chunks', result)
            self.assertIn('unknown_chunks', result)
            self.assertIn('suspicious_chunks', result)
            self.assertIn('assessment', result)
            self.assertIn('risk_contribution', result)
        finally:
            os.remove(filepath)

    def test_analyze_non_png(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Not a PNG file")
            filepath = f.name
        try:
            result = analyze_png(filepath)
            self.assertEqual(result['is_png'], False)
        finally:
            os.remove(filepath)

if __name__ == "__main__":
    unittest.main()
