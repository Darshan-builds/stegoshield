import unittest
import tempfile
import os
from PIL import Image
from core.format_validator import validate_format

class TestFormatValidator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)
        
    def test_validate_format_png(self):
        filepath = os.path.join(self.temp_dir, "test.png")
        img = Image.new("RGB", (10, 10), color="red")
        img.save(filepath, "PNG")
        
        result = validate_format(filepath)
        self.assertIn('filename', result)
        # Module returns extension without dot
        self.assertIn(result['extension'].lower(), ('png', '.png'))
        self.assertEqual(result['mismatch'], False)
        self.assertEqual(result['detected_magic'], 'PNG')
        
    def test_validate_format_mismatch(self):
        png_path = os.path.join(self.temp_dir, "test.png")
        img = Image.new("RGB", (10, 10), color="red")
        img.save(png_path, "PNG")
        
        jpg_path = os.path.join(self.temp_dir, "test_fake.jpg")
        os.rename(png_path, jpg_path)
        
        result = validate_format(jpg_path)
        self.assertEqual(result['mismatch'], True)
        self.assertIn(result['extension'].lower(), ('jpg', '.jpg'))
        self.assertEqual(result['pillow_format'], 'PNG')
        self.assertGreater(result['risk_contribution'], 0)
    
    def test_validate_nonimage(self):
        filepath = os.path.join(self.temp_dir, "test.txt")
        with open(filepath, 'w') as f:
            f.write("This is not an image")
        result = validate_format(filepath)
        self.assertIn('filename', result)

if __name__ == "__main__":
    unittest.main()
