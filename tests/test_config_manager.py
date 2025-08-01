import unittest
from config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.cm = ConfigManager()
        # Use a temporary config file for testing
        self.cm.config_file = self.cm.config_dir / "test_settings.json"
    
    def tearDown(self):
        # Remove test config file after tests
        if self.cm.config_file.exists():
            self.cm.config_file.unlink()
    
    def test_save_and_load_settings(self):
        settings = {"theme": "Dark", "default_min_size": 10}
        self.cm.save_settings(settings)
        loaded = self.cm.load_settings()
        self.assertEqual(loaded["theme"], "Dark")
        self.assertEqual(loaded["default_min_size"], 10)
