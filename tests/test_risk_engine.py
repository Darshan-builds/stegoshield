import unittest
from core.risk_engine import calculate_risk, load_config

class TestRiskEngine(unittest.TestCase):
    def test_load_config(self):
        config = load_config()
        self.assertIsInstance(config, dict)
        self.assertIn('weights', config)
        self.assertIn('max_score', config)
        
    def test_calculate_risk_empty(self):
        findings = {}
        result = calculate_risk(findings)
        
        self.assertIn('score', result)
        self.assertIn('severity', result)
        self.assertEqual(result['severity'], 'LOW')
        self.assertIn('severity_color', result)
        self.assertIn('contributors', result)
        self.assertIn('total_indicators', result)
        self.assertIn('explanation', result)
        self.assertIn('recommended_action', result)
        self.assertEqual(result['score'], 0)
        
    def test_calculate_risk_high(self):
        """Test with multiple risk indicators that sum to HIGH/CRITICAL."""
        findings = {
            'trailing_data': {'risk_contribution': 20, 'has_trailing_data': True, 'trailing_bytes': 1000},
            'embedded_data': {'risk_contribution': 25, 'total_indicators': 2, 'signatures_found': [{'type': 'PE/MZ', 'offset': 500}]},
            'format_validator': {'risk_contribution': 15, 'mismatch': True},
            'lsb_analyzer': {'risk_contribution': 15, 'anomalous_channels': ['blue']},
            'strings': {'risk_contribution': 10, 'assessment_reasons': ['suspicious keywords']},
        }
        result = calculate_risk(findings)
        
        # Total should be 20+25+15+15+10 = 85 -> CRITICAL
        self.assertGreaterEqual(result['score'], 80)
        self.assertEqual(result['severity'], 'CRITICAL')
        self.assertGreater(len(result['contributors']), 3)
    
    def test_score_capped_at_100(self):
        """Score should never exceed 100."""
        findings = {
            'trailing_data': {'risk_contribution': 50, 'has_trailing_data': True, 'trailing_bytes': 5000},
            'embedded_data': {'risk_contribution': 50, 'signatures_found': [{'type': 'PE/MZ'}]},
            'format_validator': {'risk_contribution': 30, 'mismatch': True},
            'lsb_analyzer': {'risk_contribution': 30, 'anomalous_channels': ['red', 'blue']},
        }
        result = calculate_risk(findings)
        self.assertLessEqual(result['score'], 100)
    
    def test_severity_thresholds(self):
        """Verify severity classification at boundaries."""
        # Score 0 -> LOW
        result = calculate_risk({})
        self.assertEqual(result['severity'], 'LOW')

if __name__ == "__main__":
    unittest.main()
