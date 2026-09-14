import unittest
import tempfile
import os
from core.entropy import calculate_entropy, analyze_file_entropy

class TestEntropy(unittest.TestCase):
    def test_calculate_entropy_zeroes(self):
        data = b"\x00" * 1024
        ent = calculate_entropy(data)
        self.assertEqual(ent, 0.0)

    def test_calculate_entropy_random(self):
        data = bytes(range(256)) * 4
        ent = calculate_entropy(data)
        self.assertAlmostEqual(ent, 8.0, places=1)

    def test_analyze_file_entropy(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"A" * 1024)
            filepath = f.name
            
        try:
            result = analyze_file_entropy(filepath)
            self.assertIn('overall_entropy', result)
            self.assertIn('max_entropy', result)
            self.assertIn('normalized', result)
            self.assertIn('interpretation', result)
            self.assertIn('warning_level', result)
            self.assertIn('regions', result)
            self.assertIn('note', result)
        finally:
            os.remove(filepath)

if __name__ == "__main__":
    unittest.main()
