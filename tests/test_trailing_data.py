import unittest
import tempfile
import os
import io
from PIL import Image
from core.trailing_data import detect_trailing_data

class TestTrailingData(unittest.TestCase):
    def test_no_trailing_data(self):
        filepath = os.path.join(tempfile.mkdtemp(), "clean.png")
        try:
            img = Image.new("RGB", (10, 10), color="green")
            img.save(filepath, "PNG")
            
            result = detect_trailing_data(filepath, image_format='PNG')
            self.assertEqual(result['has_trailing_data'], False)
            self.assertEqual(result['trailing_bytes'], 0)
        finally:
            os.remove(filepath)
            os.rmdir(os.path.dirname(filepath))

    def test_with_trailing_data(self):
        filepath = os.path.join(tempfile.mkdtemp(), "modified.png")
        try:
            img = Image.new("RGB", (10, 10), color="green")
            img.save(filepath, "PNG")
            
            with open(filepath, 'ab') as f:
                f.write(b"HIDDEN DATA AT THE END")
                
            result = detect_trailing_data(filepath, image_format='PNG')
            self.assertEqual(result['has_trailing_data'], True)
            self.assertGreater(result['trailing_bytes'], 0)
        finally:
            os.remove(filepath)
            os.rmdir(os.path.dirname(filepath))
    
    def test_jpeg_no_trailing(self):
        filepath = os.path.join(tempfile.mkdtemp(), "clean.jpg")
        try:
            img = Image.new("RGB", (10, 10), color="blue")
            img.save(filepath, "JPEG")
            
            result = detect_trailing_data(filepath, image_format='JPEG')
            self.assertEqual(result['has_trailing_data'], False)
        finally:
            os.remove(filepath)
            os.rmdir(os.path.dirname(filepath))
    
    def test_jpeg_with_trailing(self):
        filepath = os.path.join(tempfile.mkdtemp(), "modified.jpg")
        try:
            img = Image.new("RGB", (10, 10), color="blue")
            img.save(filepath, "JPEG")
            
            with open(filepath, 'ab') as f:
                f.write(b"APPENDED BYTES AFTER EOI")
            
            result = detect_trailing_data(filepath, image_format='JPEG')
            self.assertEqual(result['has_trailing_data'], True)
            self.assertGreater(result['trailing_bytes'], 0)
        finally:
            os.remove(filepath)
            os.rmdir(os.path.dirname(filepath))

if __name__ == "__main__":
    unittest.main()
