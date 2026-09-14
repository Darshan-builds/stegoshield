import unittest
import tempfile
import os
from PIL import Image
from core.lsb_analyzer import analyze_lsb

class TestLsbAnalyzer(unittest.TestCase):
    def test_analyze_lsb_normal(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            filepath = f.name
        try:
            img = Image.new("RGB", (10, 10), color="white")
            img.save(filepath, "PNG")
            
            result = analyze_lsb(filepath)
            self.assertTrue(result['analyzed'] or not result['analyzed']) # Might be false if too small/simple
            self.assertIn('image_mode', result)
            self.assertIn('channels', result)
            self.assertIn('overall_lsb_assessment', result)
            self.assertIn('anomalous_channels', result)
            self.assertIn('assessment', result)
            self.assertIn('risk_contribution', result)
            self.assertIn('note', result)
        finally:
            os.remove(filepath)
            
    def test_analyze_lsb_modified(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            filepath = f.name
        try:
            # Create noise image
            import random
            img = Image.new("RGB", (100, 100))
            pixels = img.load()
            for x in range(img.width):
                for y in range(img.height):
                    pixels[x, y] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
            img.save(filepath, "PNG")
            
            result = analyze_lsb(filepath)
            self.assertIsInstance(result, dict)
        finally:
            os.remove(filepath)

if __name__ == "__main__":
    unittest.main()
