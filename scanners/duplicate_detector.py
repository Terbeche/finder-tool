import hashlib
import os
from pathlib import Path
from collections import defaultdict
from PySide6.QtCore import QThread, Signal

class DuplicateDetector(QThread):
    """Thread for detecting duplicate files"""
    progress_updated = Signal(int, int, str)  # current, total, status
    duplicate_found = Signal(list)  # list of duplicate files
    detection_complete = Signal(dict)  # dict of duplicate groups
    
    def __init__(self, files, detection_method="size_name"):
        super().__init__()
        self.files = files
        self.detection_method = detection_method  # "size_name", "content_hash", "quick_hash"
        self.duplicates = defaultdict(list)
        self.stop_requested = False
    
    def run(self):
        """Run duplicate detection based on selected method"""
        if self.detection_method == "size_name":
            self._detect_by_size_and_name()
        elif self.detection_method == "content_hash":
            self._detect_by_content_hash()
        elif self.detection_method == "quick_hash":
            self._detect_by_quick_hash()
        
        if not self.stop_requested:
            # Filter out non-duplicates (groups with only one file)
            actual_duplicates = {k: v for k, v in self.duplicates.items() if len(v) > 1}
            self.detection_complete.emit(actual_duplicates)
    
    def stop(self):
        """Stop the detection process"""
        self.stop_requested = True
    
    def _detect_by_size_and_name(self):
        """Detect duplicates by file size and name"""
        self.progress_updated.emit(0, len(self.files), "Analyzing file sizes and names...")
        
        for i, file_info in enumerate(self.files):
            if self.stop_requested:
                return
            
            key = (file_info.size, file_info.name.lower())
            self.duplicates[key].append(file_info)
            
            self.progress_updated.emit(i + 1, len(self.files), f"Processed {i + 1} files...")
    
    def _detect_by_quick_hash(self):
        """Detect duplicates by quick hash (first 1KB + size)"""
        self.progress_updated.emit(0, len(self.files), "Computing quick hashes...")
        
        for i, file_info in enumerate(self.files):
            if self.stop_requested:
                return
            
            try:
                quick_hash = self._get_quick_hash(file_info.path)
                key = (file_info.size, quick_hash)
                self.duplicates[key].append(file_info)
            except Exception as e:
                # Skip files that can't be read
                continue
            
            self.progress_updated.emit(i + 1, len(self.files), f"Hashed {i + 1} files...")
    
    def _detect_by_content_hash(self):
        """Detect duplicates by full content hash (most accurate but slowest)"""
        self.progress_updated.emit(0, len(self.files), "Computing full content hashes...")
        
        for i, file_info in enumerate(self.files):
            if self.stop_requested:
                return
            
            try:
                content_hash = self._get_full_hash(file_info.path)
                self.duplicates[content_hash].append(file_info)
            except Exception as e:
                # Skip files that can't be read
                continue
            
            self.progress_updated.emit(i + 1, len(self.files), f"Hashed {i + 1} files...")
    
    def _get_quick_hash(self, file_path):
        """Get quick hash of first 1KB of file"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)  # Read first 1KB
                hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None
    
    def _get_full_hash(self, file_path):
        """Get full content hash of file"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None
