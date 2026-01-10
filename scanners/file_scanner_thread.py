from PySide6.QtCore import QThread, Signal
from pathlib import Path
from core.file_info import FileInfo
import re
from datetime import datetime, date


class FileScannerThread(QThread):
    """Thread for scanning files without blocking the UI"""
    update_progress = Signal(int, int)  # current, total
    file_found = Signal(object)  # FileInfo object
    scan_complete = Signal(list)  # List of FileInfo objects
    
    def __init__(self, directory, min_size=0, max_size=None, extensions=None, 
                 categories=None, scan_depth=None, advanced_filters=None, scan_hidden=False):
        super().__init__()
        self.directory = directory
        self.min_size = min_size * 1024 * 1024  # Convert MB to bytes
        self.max_size = max_size * 1024 * 1024 if max_size else None  # Convert MB to bytes
        self.extensions = extensions or []
        self.categories = categories or []
        self.scan_depth = scan_depth
        self.advanced_filters = advanced_filters or {}
        self.scan_hidden = scan_hidden
        self.files = []
        self.stop_requested = False
        self.pause_requested = False
        self.paused = False
        
        # Compile regex pattern for filename matching
        self.filename_pattern = None
        if 'filename_pattern' in self.advanced_filters:
            try:
                self.filename_pattern = re.compile(self.advanced_filters['filename_pattern'], re.IGNORECASE)
            except re.error:
                # Invalid regex, skip pattern matching
                self.filename_pattern = None
        
        # Text file extensions for content search
        self.text_extensions = {
            'txt', 'md', 'py', 'js', 'html', 'css', 'xml', 'json', 'csv', 
            'log', 'conf', 'ini', 'cfg', 'yml', 'yaml', 'sh', 'bat', 'ps1'
        }
    
    def run(self):
        self.scan_directory(self.directory)
        if not self.stop_requested:
            self.scan_complete.emit(self.files)
    
    def stop(self):
        self.stop_requested = True

    def pause(self):
        self.pause_requested = True
    
    def resume(self):
        self.pause_requested = False
        self.paused = False
    
    def scan_directory(self, directory, current_depth=0):
        """Recursively scan directory for files matching criteria"""
        if self.stop_requested:
            return
        
        if self.scan_depth is not None and current_depth > self.scan_depth:
            return
        
        try:
            items = list(Path(directory).iterdir())
            
            # First pass to count items for progress tracking
            total_items = len(items)
            processed = 0
            
            for item in items:
                if self.stop_requested:
                    return
                
                # Skip symlinks to avoid infinite loops
                if item.is_symlink():
                    continue
                
                # Skip hidden files/directories unless enabled
                if not self.scan_hidden and item.name.startswith('.'):
                    continue
                while self.pause_requested and not self.stop_requested:
                    if not self.paused:
                        self.paused = True
                    self.msleep(100)  # Sleep for 100ms to avoid CPU spin
                
                self.paused = False
                
                processed += 1
                self.update_progress.emit(processed, total_items)
                
                try:
                    if item.is_file():
                        file_size = item.stat().st_size
                        file_mtime = datetime.fromtimestamp(item.stat().st_mtime)
                        
                        # Check size constraints
                        if self.min_size and file_size < self.min_size:
                            continue
                        if self.max_size and file_size > self.max_size:
                            continue
                        
                        # Check date range filter
                        if not self._check_date_filter(file_mtime):
                            continue
                        
                        # Get file extension and check if it matches our criteria
                        extension = item.suffix.lstrip('.').lower()
                        if self.extensions and extension not in self.extensions:
                            continue
                        
                        # Check filename pattern filter
                        if not self._check_filename_pattern(item.name):
                            continue
                        
                        # Find matching category
                        category = None
                        for cat in self.categories:
                            if cat.matches(extension):
                                category = cat
                                break
                        
                        # Check content search filter (for text files)
                        if not self._check_content_search(item, extension):
                            continue
                        
                        # Create FileInfo object
                        file_info = FileInfo(
                            str(item.absolute()),
                            item.name,
                            extension,
                            file_size,
                            file_mtime,
                            category
                        )
                        
                        self.files.append(file_info)
                        self.file_found.emit(file_info)
                    
                    elif item.is_dir() and not item.name.startswith('.'):
                        # Process subdirectories
                        self.scan_directory(item, current_depth + 1)
                
                except (PermissionError, FileNotFoundError) as e:
                    # Skip files/directories we can't access
                    pass
                    
        except (PermissionError, FileNotFoundError) as e:
            # Skip directories we can't access
            pass
    
    def _check_date_filter(self, file_mtime):
        """Check if file modification time matches date filter"""
        if 'date_from' not in self.advanced_filters and 'date_to' not in self.advanced_filters:
            return True
        
        file_date = file_mtime.date()
        
        if 'date_from' in self.advanced_filters:
            if file_date < self.advanced_filters['date_from']:
                return False
        
        if 'date_to' in self.advanced_filters:
            if file_date > self.advanced_filters['date_to']:
                return False
        
        return True
    
    def _check_filename_pattern(self, filename):
        """Check if filename matches regex pattern"""
        if not self.filename_pattern:
            return True
        
        return bool(self.filename_pattern.search(filename))
    
    def _check_content_search(self, file_path, extension):
        """Check if file content contains search term"""
        if 'content_search' not in self.advanced_filters:
            return True
        
        # Only search in text files
        if extension not in self.text_extensions:
            return True  # Skip content search for non-text files
        
        search_term = self.advanced_filters['content_search'].lower()
        
        try:
            # Read file and search for content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read first 1MB to avoid memory issues with large files
                content = f.read(1024 * 1024).lower()
                return search_term in content
        except (IOError, UnicodeDecodeError, PermissionError):
            # Skip files that can't be read
            return True

