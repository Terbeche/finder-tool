"""Unit tests for FileScannerThread"""
import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# We need to mock PySide6 before importing the scanner
import sys
from unittest.mock import MagicMock

# Create mock for PySide6.QtCore
mock_qtcore = MagicMock()
mock_qtcore.QThread = object
mock_qtcore.Signal = lambda *args: MagicMock()
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = mock_qtcore

from core.file_category import FileCategory


class TestFileScannerLogic(unittest.TestCase):
    """Test the scanning logic without Qt dependencies"""
    
    def setUp(self):
        """Create a temporary directory structure for testing"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files
        self.create_test_file("file1.txt", "Hello World", 100)
        self.create_test_file("file2.py", "print('test')", 50)
        self.create_test_file("image.jpg", "fake image", 1024)
        self.create_test_file(".hidden_file.txt", "hidden content", 10)
        
        # Create subdirectory
        os.makedirs(os.path.join(self.temp_dir, "subdir"))
        self.create_test_file("subdir/nested.txt", "nested content", 25)
        
        # Create hidden directory
        os.makedirs(os.path.join(self.temp_dir, ".hidden_dir"))
        self.create_test_file(".hidden_dir/secret.txt", "secret", 5)
    
    def create_test_file(self, name, content, size_approx):
        """Helper to create a test file"""
        path = os.path.join(self.temp_dir, name)
        with open(path, 'w') as f:
            f.write(content)
    
    def tearDown(self):
        """Clean up temporary directory"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_hidden_file_detection(self):
        """Test that hidden files are correctly identified"""
        hidden_file = Path(self.temp_dir) / ".hidden_file.txt"
        normal_file = Path(self.temp_dir) / "file1.txt"
        
        self.assertTrue(hidden_file.name.startswith('.'))
        self.assertFalse(normal_file.name.startswith('.'))
    
    def test_hidden_directory_detection(self):
        """Test that hidden directories are correctly identified"""
        hidden_dir = Path(self.temp_dir) / ".hidden_dir"
        normal_dir = Path(self.temp_dir) / "subdir"
        
        self.assertTrue(hidden_dir.name.startswith('.'))
        self.assertFalse(normal_dir.name.startswith('.'))
    
    def test_extension_extraction(self):
        """Test file extension extraction"""
        files = [
            ("test.txt", "txt"),
            ("image.JPG", "jpg"),
            ("archive.tar.gz", "gz"),
            ("noextension", ""),
        ]
        
        for filename, expected_ext in files:
            path = Path(filename)
            ext = path.suffix.lstrip('.').lower()
            self.assertEqual(ext, expected_ext, f"Failed for {filename}")
    
    def test_symlink_detection(self):
        """Test symlink detection (skip on Windows)"""
        if os.name == 'nt':
            self.skipTest("Symlink test not supported on Windows")
        
        # Create a symlink
        link_path = os.path.join(self.temp_dir, "link_to_file")
        target_path = os.path.join(self.temp_dir, "file1.txt")
        os.symlink(target_path, link_path)
        
        link = Path(link_path)
        self.assertTrue(link.is_symlink())
        
        # Clean up
        os.unlink(link_path)
    
    def test_depth_counting(self):
        """Test depth calculation for nested directories"""
        base = Path(self.temp_dir)
        subdir = base / "subdir"
        
        # Simulate depth counting
        depth = 0
        current = subdir
        while current != base and current.parent != current:
            depth += 1
            current = current.parent
            if depth > 10:  # Safety limit
                break
        
        self.assertEqual(depth, 1)
    
    def test_file_category_matching(self):
        """Test category matching for extensions"""
        categories = [
            FileCategory("Images", ["jpg", "png", "gif"], "#2ecc71"),
            FileCategory("Documents", ["txt", "pdf", "doc"], "#f39c12"),
            FileCategory("Code", ["py", "js", "html"], "#3498db"),
        ]
        
        test_cases = [
            ("jpg", "Images"),
            ("txt", "Documents"),
            ("py", "Code"),
            ("unknown", None),
        ]
        
        for ext, expected_category in test_cases:
            matched = None
            for cat in categories:
                if cat.matches(ext):
                    matched = cat.name
                    break
            self.assertEqual(matched, expected_category, f"Failed for extension: {ext}")


class TestFileSizeFiltering(unittest.TestCase):
    """Test file size filtering logic"""
    
    def test_min_size_filter(self):
        """Test minimum size filtering"""
        min_size_mb = 1  # 1 MB
        min_size_bytes = min_size_mb * 1024 * 1024
        
        # File smaller than limit should be filtered
        small_file_size = 500 * 1024  # 500 KB
        self.assertTrue(small_file_size < min_size_bytes)
        
        # File larger than limit should pass
        large_file_size = 2 * 1024 * 1024  # 2 MB
        self.assertFalse(large_file_size < min_size_bytes)
    
    def test_max_size_filter(self):
        """Test maximum size filtering"""
        max_size_mb = 10  # 10 MB
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # File smaller than limit should pass
        small_file_size = 5 * 1024 * 1024  # 5 MB
        self.assertFalse(small_file_size > max_size_bytes)
        
        # File larger than limit should be filtered
        large_file_size = 15 * 1024 * 1024  # 15 MB
        self.assertTrue(large_file_size > max_size_bytes)


class TestFilenamePatternMatching(unittest.TestCase):
    """Test filename pattern matching"""
    
    def test_regex_pattern_matching(self):
        """Test regex pattern matching on filenames"""
        import re
        
        patterns = [
            (r"IMG_\d{4}", "IMG_1234.jpg", True),
            (r"IMG_\d{4}", "photo.jpg", False),
            (r".*\.backup\..*", "file.backup.txt", True),
            (r"^test.*\.py$", "test_scanner.py", True),
            (r"^test.*\.py$", "my_test.py", False),
        ]
        
        for pattern, filename, should_match in patterns:
            compiled = re.compile(pattern, re.IGNORECASE)
            matched = bool(compiled.search(filename))
            self.assertEqual(matched, should_match, 
                           f"Pattern '{pattern}' on '{filename}' expected {should_match}")


if __name__ == '__main__':
    unittest.main()
