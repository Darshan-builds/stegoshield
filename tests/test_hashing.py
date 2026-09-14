import unittest
import tempfile
import os
import hashlib
from core.hashing import compute_hashes

class TestHashing(unittest.TestCase):
    def test_compute_hashes(self):
        content = b"StegoShield Test"
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(content)
            filepath = f.name
        
        try:
            result = compute_hashes(filepath)
            self.assertEqual(result['md5'], hashlib.md5(content).hexdigest())
            self.assertEqual(result['sha256'], hashlib.sha256(content).hexdigest())
            self.assertIn('sha1', result)
            self.assertIn('sha512', result)
            self.assertIn('sha3_256', result)
            self.assertIn('primary', result)
            self.assertIn('note', result)
        finally:
            os.remove(filepath)

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            filepath = f.name
            
        try:
            result = compute_hashes(filepath)
            self.assertEqual(result['md5'], hashlib.md5(b"").hexdigest())
        finally:
            os.remove(filepath)

    def test_nonexistent_file(self):
        result = compute_hashes("does_not_exist_12345.bin")
        self.assertIsInstance(result, dict)

if __name__ == "__main__":
    unittest.main()
