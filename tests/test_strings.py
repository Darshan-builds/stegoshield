import unittest
import tempfile
import os
from core.strings import analyze_strings

class TestStrings(unittest.TestCase):
    def test_analyze_strings(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            # Use keywords that are in the SUSPICIOUS_KEYWORDS list
            f.write(b"This is a normal string\x00\x01\x02http://malicious.com\x00powershell -exec bypass\x00192.168.1.1")
            filepath = f.name
        try:
            result = analyze_strings(filepath, min_length=4)
            self.assertIn('total_strings', result)
            self.assertIn('ascii_strings', result)
            self.assertIn('urls', result)
            self.assertIn('ip_addresses', result)
            self.assertIn('suspicious_keywords', result)
            
            # Check URLs detected
            self.assertTrue(any("http://malicious.com" in url for url in result['urls']),
                          f"Expected URL not found. URLs: {result['urls']}")
            # Check IPs detected
            self.assertTrue(any("192.168.1.1" in ip for ip in result['ip_addresses']),
                          f"Expected IP not found. IPs: {result['ip_addresses']}")
            # 'powershell' is in SUSPICIOUS_KEYWORDS, 'password' is not
            kw_lower = [str(kw).lower() for kw in result['suspicious_keywords']]
            self.assertTrue(any("powershell" in kw for kw in kw_lower),
                          f"Expected 'powershell' keyword. Got: {result['suspicious_keywords']}")
        finally:
            os.remove(filepath)
    
    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            filepath = f.name
        try:
            result = analyze_strings(filepath, min_length=4)
            self.assertEqual(result['total_strings'], 0)
        finally:
            os.remove(filepath)
    
    def test_binary_only(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(bytes(range(256)) * 4)
            filepath = f.name
        try:
            result = analyze_strings(filepath, min_length=4)
            self.assertIsInstance(result['total_strings'], int)
        finally:
            os.remove(filepath)

if __name__ == "__main__":
    unittest.main()
