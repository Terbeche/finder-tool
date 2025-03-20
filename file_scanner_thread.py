from PySide6.QtCore import QThread, Signal
from pathlib import Path
from file_info import FileInfo
from datetime import datetime


class FileScannerThread(QThread):
    """Thread for scanning files without blocking the UI"""
    update_progress = Signal(int, int)  # current, total
    file_found = Signal(object)  # FileInfo object
    scan_complete = Signal(list)  # List of FileInfo objects
    
    def __init__(self, directory, min_size=0, max_size=None, extensions=None, 
                 categories=None, scan_depth=None):
        super().__init__()
        self.directory = directory
        self.min_size = min_size * 1024 * 1024  # Convert MB to bytes
        self.max_size = max_size * 1024 * 1024 if max_size else None  # Convert MB to bytes
        self.extensions = extensions or []
        self.categories = categories or []
        self.scan_depth = scan_depth
        self.files = []
        self.stop_requested = False
        self.pause_requested = False
        self.paused = False
    
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
                
                # Handle pause if requested
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
                        
                        # Check size constraints
                        if self.min_size and file_size < self.min_size:
                            continue
                        if self.max_size and file_size > self.max_size:
                            continue
                        
                        # Get file extension and check if it matches our criteria
                        extension = item.suffix.lstrip('.').lower()
                        if self.extensions and extension not in self.extensions:
                            continue
                        
                        # Find matching category
                        category = None
                        for cat in self.categories:
                            if cat.matches(extension):
                                category = cat
                                break
                        
                        # Create FileInfo object
                        file_info = FileInfo(
                            str(item.absolute()),
                            item.name,
                            extension,
                            file_size,
                            datetime.fromtimestamp(item.stat().st_mtime),
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

