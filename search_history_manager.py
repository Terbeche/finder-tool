import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

@dataclass
class SearchHistoryEntry:
    """Represents a search history entry"""
    timestamp: str  # ISO format timestamp
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
    
    # Results
    results: Optional[Dict[str, Any]] = None
    
    # For backward compatibility with older saved data
    files_found: int = 0
    total_size: int = 0
    search_duration: float = 0.0

class SearchHistoryManager:
    """Manages search history entries"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.history: List[SearchHistoryEntry] = []
        self.max_entries = 100  # Keep last 100 searches
        self.load_history()
    
    def load_history(self):
        """Load search history from config"""
        data = self.config_manager._load_config_data()
        
        if "search_history" in data:
            for entry_data in data["search_history"]:
                try:
                    # Filter out any unknown fields for backward compatibility
                    valid_fields = {
                        'timestamp', 'directory', 'category', 'min_size', 'max_size', 'max_depth',
                        'date_filter_enabled', 'date_from', 'date_to', 'pattern_filter_enabled', 
                        'filename_pattern', 'content_filter_enabled', 'content_search', 'results',
                        'files_found', 'total_size', 'search_duration'
                    }
                    
                    # Only include fields that exist in the SearchHistoryEntry dataclass
                    filtered_data = {k: v for k, v in entry_data.items() if k in valid_fields}
                    
                    entry = SearchHistoryEntry(**filtered_data)
                    self.history.append(entry)
                except Exception as e:
                    # Skip invalid entries but don't crash
                    print(f"Skipping invalid search history entry: {e}")
                    continue
    
    def save_history(self):
        """Save search history to config"""
        data = self.config_manager._load_config_data()
        data["search_history"] = [asdict(entry) for entry in self.history]
        self.config_manager._save_config_data(data)
    
    def add_search(self, search_config: Dict[str, Any], results_summary: Dict[str, Any]):
        """Add a search to history"""
        try:
            entry = SearchHistoryEntry(
                timestamp=datetime.now().isoformat(),
                directory=search_config["directory"],
                category=search_config["category"],
                min_size=search_config["min_size"],
                max_size=search_config["max_size"],
                max_depth=search_config["max_depth"],
                date_filter_enabled=search_config["date_filter_enabled"],
                date_from=search_config["date_from"],
                date_to=search_config["date_to"],
                pattern_filter_enabled=search_config["pattern_filter_enabled"],
                filename_pattern=search_config["filename_pattern"],
                content_filter_enabled=search_config["content_filter_enabled"],
                content_search=search_config["content_search"],
                results=results_summary
            )
            
            self.history.append(entry)
            
            # Limit the number of entries
            if len(self.history) > self.max_entries:
                self.history = self.history[-self.max_entries:]
            
            # Remove exact duplicates (same configuration and directory)
            seen_configs = set()
            unique_history = []
            
            for hist_entry in self.history:
                config_signature = (
                    hist_entry.directory,
                    hist_entry.category,
                    hist_entry.min_size,
                    hist_entry.max_size,
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
    
    def get_entries(self) -> List[SearchHistoryEntry]:
        """Get all search history entries"""
        return self.history
    
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
    
    def delete_entry(self, timestamp: str) -> bool:
        """Delete a search history entry by timestamp"""
        original_count = len(self.history)
        self.history = [e for e in self.history if e.timestamp != timestamp]
        
        if len(self.history) < original_count:
            self.save_history()
            return True
        return False
    
    def clear_history(self):
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
        
        # Calculate statistics from results
        total_files = 0
        total_size = 0
        total_time = 0
        valid_results = 0
        
        for entry in self.history:
            if entry.results:
                if "files_found" in entry.results:
                    total_files += entry.results["files_found"]
                if "total_size" in entry.results:
                    total_size += entry.results["total_size"]
                if "search_duration" in entry.results:
                    total_time += entry.results["search_duration"]
                    valid_results += 1
        
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
            "average_search_time": total_time / valid_results if valid_results > 0 else 0,
            "most_searched_directory": most_searched_dir,
            "most_used_category": most_used_category
        }
