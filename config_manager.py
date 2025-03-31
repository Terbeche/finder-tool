import json
import os
from pathlib import Path
import platform
from file_category import FileCategory

class ConfigManager:
    """Manages application configuration and persistence"""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "settings.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._last_saved_settings = None
    
    def _get_config_dir(self):
        """Get platform-specific configuration directory"""
        if platform.system() == "Windows":
            base_dir = Path(os.environ.get("APPDATA", ""))
            return base_dir / "SmartFileManager"
        elif platform.system() == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "SmartFileManager"
        else:  # Linux and others
            xdg_config = os.environ.get("XDG_CONFIG_HOME", "")
            if xdg_config:
                base_dir = Path(xdg_config)
            else:
                base_dir = Path.home() / ".config"
            print(f"Using XDG config directory: {base_dir}")
            return base_dir / "smartfilemanager"
    
    def save_categories(self, categories):
        """Save file categories to config file"""
        data = self._load_config_data()
        
        # Convert categories to serializable format
        serialized_categories = []
        for category in categories:
            serialized_categories.append({
                "name": category.name,
                "extensions": category.extensions,
                "color": category.color
            })
        
        data["categories"] = serialized_categories
        self._save_config_data(data)
    
    def load_categories(self, default_categories):
        """Load file categories from config file"""
        data = self._load_config_data()
        
        if "categories" not in data:
            return default_categories.copy()
        
        categories = []
        for cat_data in data["categories"]:
            category = FileCategory(
                cat_data["name"],
                cat_data.get("extensions", []),
                cat_data.get("color", "#3498db")
            )
            categories.append(category)
        
        return categories if categories else default_categories.copy()
    
    def save_settings(self, settings):
        """Save general application settings"""
        try:
            data = self._load_config_data()
            data["settings"] = settings
            self._save_config_data(data)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self):
        """Load general application settings"""
        data = self._load_config_data()
        
        # Default settings
        default_settings = {
            "auto_discover": True,
            "default_min_size": 0,
            "default_max_depth": 15,
            "last_directory": str(Path.home())
        }
        
        if "settings" not in data:
            return default_settings
        
        # Update defaults with stored settings
        settings = default_settings.copy()
        settings.update(data["settings"])
        return settings
    
    def _load_config_data(self):
        """Load data from config file"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Handle corrupted config file
            return {}
    
    def _save_config_data(self, data):
        """Save data to config file with error handling and atomic writes"""
        try:
            # Write to temporary file first
            temp_file = self.config_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # Atomic replace
            temp_file.replace(self.config_file)
            print(f"Configuration saved to {self.config_file}")
            return True
        except IOError as e:
            print(f"Error saving configuration: {str(e)}")
            return False