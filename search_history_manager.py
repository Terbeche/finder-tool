import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

@dataclass
class SearchHistoryEntry:
    """Represents a search history entry"""
    timestamp: str
    directory: str
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
    
    # Results summary
    files_found: int = 0
    total_size: int = 0
    search_duration: float = 0.0  # in seconds
    
    # Optional description
    description: str = ""

class SearchHistoryManager:
    """Manages search history storage and retrieval"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.history: List[SearchHistoryEntry] = []
        self.max_history_entries = 100  # Keep last 100 searches
        self.load_history()
    
    def load_history(self):
        """Load search history from config"""
        data = self.config_manager._load_config_data()
        
        if "search_history" in data:
            try:
                self.history = [
                    SearchHistoryEntry(**entry_data) 
                    for entry_data in data["search_history"]
                ]
                # Sort by timestamp, newest first
                self.history.sort(key=lambda x: x.timestamp, reverse=True)
            except Exception as e:
                print(f"Error loading search history: {e}")
                self.history = []
    
    def save_history(self):
        """Save search history to config"""
        try:
            # Limit history size
            if len(self.history) > self.max_history_entries:
                self.history = self.history[:self.max_history_entries]
            
            data = self.config_manager._load_config_data()
            data["search_history"] = [asdict(entry) for entry in self.history]
            self.config_manager._save_config_data(data)
        except Exception as e:
            print(f"Error saving search history: {e}")
    
    def add_search(self, search_config: Dict[str, Any], results_summary: Dict[str, Any], description: str = "") -> bool:
        """Add a new search to history"""
        try:
            entry = SearchHistoryEntry(
                timestamp=datetime.now().isoformat(),
                description=description,
                **search_config,
                **results_summary
            )
            
            # Add to beginning of list (newest first)
            self.history.insert(0, entry)
            
            # Remove duplicates based on search parameters (keep newest)
            seen_configs = set()
            unique_history = []
            
            for hist_entry in self.history:
                # Create a config signature for deduplication
                config_signature = (
                    hist_entry.directory,
                    hist_entry.category,
                    hist_entry.min_size,
                    hist_entry.max_size,
                    hist_entry.max_depth,
                    hist_entry.date_filter_enabled,
                    hist_entry.date_from,
                    hist_entry.date_to,
                    hist_entry.pattern_filter_enabled,
                    hist_entry.filename_pattern,
                    hist_entry.content_filter_enabled,
                    hist_entry.content_search
                )
                
                if config_signature not in seen_configs:
                    seen_configs.add(config_signature)
                    unique_history.append(hist_entry)
            
            self.history = unique_history
            self.save_history()
            return True
            
        except Exception as e:
            print(f"Error adding search to history: {e}")
            return False
    
    def get_history(self, limit: Optional[int] = None) -> List[SearchHistoryEntry]:
        """Get search history, optionally limited"""
        if limit:
            return self.history[:limit]
        return self.history.copy()
    
    def get_recent_searches(self, days: int = 7) -> List[SearchHistoryEntry]:
        """Get searches from the last N days"""
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        cutoff_str = cutoff_date.isoformat()
        
        return [entry for entry in self.history if entry.timestamp >= cutoff_str]
    
    def get_popular_directories(self, limit: int = 10) -> List[tuple]:
        """Get most frequently searched directories"""
        directory_counts = {}
        
        for entry in self.history:
            directory_counts[entry.directory] = directory_counts.get(entry.directory, 0) + 1
        
        # Sort by count, descending
        sorted_dirs = sorted(directory_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_dirs[:limit]
    
    def get_popular_searches(self, limit: int = 10) -> List[SearchHistoryEntry]:
        """Get most common search configurations"""
        # Group by search configuration
        config_groups = {}
        
        for entry in self.history:
            config_key = (
                entry.category,
                entry.min_size,
                entry.max_size,
                entry.pattern_filter_enabled,
                entry.filename_pattern,
                entry.content_filter_enabled,
                entry.content_search
            )
            
            if config_key not in config_groups:
                config_groups[config_key] = []
            config_groups[config_key].append(entry)
        
        # Sort by frequency and get the most recent entry from each group
        popular_configs = sorted(config_groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        return [group[0] for _, group in popular_configs[:limit]]
    
    def remove_entry(self, timestamp: str) -> bool:
        """Remove a specific history entry"""
        original_count = len(self.history)
        self.history = [entry for entry in self.history if entry.timestamp != timestamp]
        
        if len(self.history) < original_count:
            self.save_history()
            return True
        return False
    
    def clear_history(self) -> bool:
        """Clear all search history"""
        try:
            self.history = []
            self.save_history()
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False
    
    def export_history(self, file_path: str) -> bool:
        """Export search history to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(entry) for entry in self.history], f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting history: {e}")
            return False
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get statistics about search history"""
        if not self.history:
            return {
                "total_searches": 0,
                "average_files_found": 0,
                "total_data_scanned": 0,
                "average_search_time": 0,
                "most_searched_directory": "None",
                "most_used_category": "None"
            }
        
        total_searches = len(self.history)
        total_files = sum(entry.files_found for entry in self.history)
        total_size = sum(entry.total_size for entry in self.history)
        total_time = sum(entry.search_duration for entry in self.history)
        
        # Most common directory
        dir_counts = {}
        for entry in self.history:
            dir_counts[entry.directory] = dir_counts.get(entry.directory, 0) + 1
        most_searched_dir = max(dir_counts.items(), key=lambda x: x[1])[0] if dir_counts else "None"
        
        # Most common category
        cat_counts = {}
        for entry in self.history:
            cat_counts[entry.category] = cat_counts.get(entry.category, 0) + 1
        most_used_category = max(cat_counts.items(), key=lambda x: x[1])[0] if cat_counts else "None"
        
        return {
            "total_searches": total_searches,
            "average_files_found": total_files / total_searches if total_searches > 0 else 0,
            "total_data_scanned": total_size,
            "average_search_time": total_time / total_searches if total_searches > 0 else 0,
            "most_searched_directory": most_searched_dir,
            "most_used_category": most_used_category
        }
