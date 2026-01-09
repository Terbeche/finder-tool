import unittest
from managers.usage_analytics import UsageAnalytics
import tempfile
import os

class TestUsageAnalytics(unittest.TestCase):
    def setUp(self):
        self.analytics = UsageAnalytics()
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
    
    def tearDown(self):
        # Remove temporary file
        os.unlink(self.temp_file.name)
    
    def test_record_access(self):
        self.analytics.record_access(self.temp_file.name)
        self.assertIn(self.temp_file.name, self.analytics.usage_data)
        self.assertEqual(self.analytics.usage_data[self.temp_file.name]["access_count"], 1)
        
        # Record a second access
        self.analytics.record_access(self.temp_file.name)
        self.assertEqual(self.analytics.usage_data[self.temp_file.name]["access_count"], 2)
    
    def test_get_access_statistics(self):
        self.analytics.record_access(self.temp_file.name)
        stats = self.analytics.get_access_statistics()
        
        self.assertEqual(stats["total_files"], 1)
        self.assertEqual(stats["accessed_files"], 1)
        self.assertEqual(stats["never_accessed"], 0)
        self.assertEqual(stats["access_rate"], 100.0)
