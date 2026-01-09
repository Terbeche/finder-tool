
class FileCategory:
    """Class to manage file extension categories"""
    def __init__(self, name, extensions=None, color=None):
        self.name = name
        self.extensions = extensions or []
        self.color = color or "#3498db"  # Default blue
    
    def matches(self, file_extension):
        """Check if the given extension belongs to this category"""
        return file_extension.lower() in [ext.lower() for ext in self.extensions]

    def add_extension(self, extension):
        """Add a new extension to this category"""
        if extension.lower() not in [ext.lower() for ext in self.extensions]:
            self.extensions.append(extension.lower())
            return True
        return False