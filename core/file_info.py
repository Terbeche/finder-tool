
class FileInfo:
    """Class to store file information"""
    def __init__(self, path, name, extension, size, modified_date, category=None):
        self.path = path
        self.name = name
        self.extension = extension.lower() if extension else ""
        self.size = size  # Size in bytes
        self.modified_date = modified_date
        self.category = category
        self.selected = False
    
    def get_size_str(self):
        """Return human-readable size string"""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        elif self.size < 1024 * 1024 * 1024:
            return f"{self.size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.size / (1024 * 1024 * 1024):.2f} GB"
