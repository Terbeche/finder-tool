import unittest
from core.file_category import FileCategory

class TestFileCategory(unittest.TestCase):
    def test_matches(self):
        cat = FileCategory("Images", ["jpg", "png", "gif"])
        self.assertTrue(cat.matches("jpg"))
        self.assertTrue(cat.matches("GIF"))
        self.assertFalse(cat.matches("mp4"))
    
    def test_add_extension(self):
        cat = FileCategory("Docs", ["txt"])
        self.assertTrue(cat.add_extension("md"))
        self.assertFalse(cat.add_extension("txt"))
