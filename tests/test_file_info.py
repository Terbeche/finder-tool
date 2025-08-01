import unittest
from file_info import FileInfo
from datetime import datetime

class TestFileInfo(unittest.TestCase):
    def test_size_str(self):
        fi = FileInfo("/tmp/test.txt", "test.txt", "txt", 512, datetime.now())
        self.assertEqual(fi.get_size_str(), "512 B")
        fi.size = 2048
        self.assertEqual(fi.get_size_str(), "2.0 KB")
        fi.size = 2 * 1024 * 1024
        self.assertEqual(fi.get_size_str(), "2.0 MB")
        fi.size = 3 * 1024 * 1024 * 1024
        self.assertEqual(fi.get_size_str(), "3.00 GB")
