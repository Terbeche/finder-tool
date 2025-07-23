import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

@dataclass
class SearchPreset:
    """Represents a saved search configuration"""
    name: str
    description: str = ""
    category: str = "All Files"
    min_size: int = 0
    max_size: int = 0
    max_depth: int = 15
    
    # Advanced filters
    date_filter_enabled: bool = False
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    pattern_filter_enabled: bool = False
    filename_pattern: str = ""
    content_filter_enabled: bool = False
    content_search: str = ""
    
    created_at: Optional[str] = None
    last_used: Optional[str] = None

@dataclass
class DirectoryBookmark:
    """Represents a bookmarked directory"""
    name: str
    path: str
    description: str = ""
    created_at: Optional[str] = None
    last_used: Optional[str] = None
    usage_count: int = 0

class BookmarkManager:
    """Manages directory bookmarks and search presets"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.bookmarks: List[DirectoryBookmark] = []
        self.presets: List[SearchPreset] = []
        self.load_bookmarks()
    
    def load_bookmarks(self):
        """Load bookmarks and presets from config"""
        data = self.config_manager._load_config_data()
        
        # Load directory bookmarks
        if "bookmarks" in data:
            self.bookmarks = [
                DirectoryBookmark(**bookmark_data) 
                for bookmark_data in data["bookmarks"]
            ]
        
        # Load search presets
        if "search_presets" in data:
            self.presets = [
                SearchPreset(**preset_data) 
                for preset_data in data["search_presets"]
            ]
    
    def save_bookmarks(self):
        """Save bookmarks and presets to config"""
        data = self.config_manager._load_config_data()
        data["bookmarks"] = [asdict(bookmark) for bookmark in self.bookmarks]
        data["search_presets"] = [asdict(preset) for preset in self.presets]
        self.config_manager._save_config_data(data)
    
    # Directory Bookmark methods
    def add_bookmark(self, name: str, path: str, description: str = "") -> bool:
        """Add a new directory bookmark"""
        # Check if bookmark already exists
        if any(b.path == path for b in self.bookmarks):
            return False
        
        bookmark = DirectoryBookmark(
            name=name,
            path=path,
            description=description,
            created_at=datetime.now().isoformat(),
            last_used=None,
            usage_count=0
        )
        
        self.bookmarks.append(bookmark)
        self.save_bookmarks()
        return True
    
    def remove_bookmark(self, path: str) -> bool:
        """Remove a directory bookmark"""
        original_count = len(self.bookmarks)
        self.bookmarks = [b for b in self.bookmarks if b.path != path]
        
        if len(self.bookmarks) < original_count:
            self.save_bookmarks()
            return True
        return False
    
    def update_bookmark(self, path: str, name: str = None, description: str = None) -> bool:
        """Update an existing bookmark"""
        for bookmark in self.bookmarks:
            if bookmark.path == path:
                if name is not None:
                    bookmark.name = name
                if description is not None:
                    bookmark.description = description
                self.save_bookmarks()
                return True
        return False
    
    def use_bookmark(self, path: str):
        """Mark a bookmark as used (update stats)"""
        for bookmark in self.bookmarks:
            if bookmark.path == path:
                bookmark.last_used = datetime.now().isoformat()
                bookmark.usage_count += 1
                self.save_bookmarks()
                break
    
    def get_bookmarks(self) -> List[DirectoryBookmark]:
        """Get all directory bookmarks sorted by usage"""
        return sorted(self.bookmarks, key=lambda b: b.usage_count, reverse=True)
    
    # Search Preset methods
    def add_preset(self, name: str, search_config: Dict[str, Any], description: str = "") -> bool:
        """Add a new search preset"""
        # Check if preset already exists
        if any(p.name == name for p in self.presets):
            return False
        
        preset = SearchPreset(
            name=name,
            description=description,
            created_at=datetime.now().isoformat(),
            last_used=None,
            **search_config
        )
        
        self.presets.append(preset)
        self.save_bookmarks()
        return True
    
    def remove_preset(self, name: str) -> bool:
        """Remove a search preset"""
        original_count = len(self.presets)
        self.presets = [p for p in self.presets if p.name != name]
        
        if len(self.presets) < original_count:
            self.save_bookmarks()
            return True
        return False
    
    def update_preset(self, name: str, search_config: Dict[str, Any] = None, description: str = None) -> bool:
        """Update an existing preset"""
        for preset in self.presets:
            if preset.name == name:
                if description is not None:
                    preset.description = description
                if search_config is not None:
                    # Update search configuration
                    for key, value in search_config.items():
                        if hasattr(preset, key):
                            setattr(preset, key, value)
                self.save_bookmarks()
                return True
        return False
    
    def use_preset(self, name: str):
        """Mark a preset as used"""
        for preset in self.presets:
            if preset.name == name:
                preset.last_used = datetime.now().isoformat()
                self.save_bookmarks()
                break
    
    def get_presets(self) -> List[SearchPreset]:
        """Get all search presets sorted by last used"""
        return sorted(self.presets, 
                     key=lambda p: p.last_used or "1900-01-01", 
                     reverse=True)
    
    def get_preset_by_name(self, name: str) -> Optional[SearchPreset]:
        """Get a specific preset by name"""
        for preset in self.presets:
            if preset.name == name:
                return preset
        return None
    
    def update_bookmark_full(self, old_path: str, name: str, new_path: str, description: str = "") -> bool:
        """Update a bookmark with potentially new path"""
        for i, bookmark in enumerate(self.bookmarks):
            if bookmark.path == old_path:
                # Check if new path conflicts with other bookmarks
                if new_path != old_path and any(b.path == new_path for b in self.bookmarks):
                    return False
                
                # Update bookmark
                bookmark.name = name
                bookmark.path = new_path
                bookmark.description = description
                self.save_bookmarks()
                return True
        return False
    
    def update_preset_full(self, old_name: str, new_name: str, search_config: Dict[str, Any], description: str = "") -> bool:
        """Update a preset with potentially new name and full configuration"""
        for preset in self.presets:
            if preset.name == old_name:
                # Check if new name conflicts with other presets
                if new_name != old_name and any(p.name == new_name for p in self.presets):
                    return False
                
                # Update preset
                preset.name = new_name
                preset.description = description
                
                # Update all configuration fields
                for key, value in search_config.items():
                    if hasattr(preset, key):
                        setattr(preset, key, value)
                
                self.save_bookmarks()
                return True
        return False
