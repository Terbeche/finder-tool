import os
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

class UsageAnalytics:
    """Tracks and analyzes file usage patterns."""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.usage_data = defaultdict(lambda: {"access_count": 0, "last_accessed": None})
        self.load_usage_data()
    
    def load_usage_data(self):
        """Load usage data from config file"""
        if not self.config_manager:
            return
        
        data = self.config_manager._load_config_data()
        if "usage_analytics" in data:
            # Convert datetime strings back to datetime objects
            for file_path, file_data in data["usage_analytics"].items():
                self.usage_data[file_path] = {
                    "access_count": file_data.get("access_count", 0),
                    "last_accessed": datetime.fromisoformat(file_data["last_accessed"]) if file_data.get("last_accessed") else None
                }
    
    def save_usage_data(self):
        """Save usage data to config file"""
        if not self.config_manager:
            return
        
        data = self.config_manager._load_config_data()
        
        # Convert datetime objects to strings for JSON serialization
        serializable_data = {}
        for file_path, file_data in self.usage_data.items():
            serializable_data[file_path] = {
                "access_count": file_data["access_count"],
                "last_accessed": file_data["last_accessed"].isoformat() if file_data["last_accessed"] else None
            }
        
        data["usage_analytics"] = serializable_data
        self.config_manager._save_config_data(data)
    
    def record_access(self, file_path):
        """Record a file access event."""
        file_path = os.path.abspath(file_path)
        now = datetime.now()
        self.usage_data[file_path]["access_count"] += 1
        self.usage_data[file_path]["last_accessed"] = now
        
        # Save periodically (every 10 accesses to avoid too frequent writes)
        if sum(data["access_count"] for data in self.usage_data.values()) % 10 == 0:
            self.save_usage_data()
    
    def get_frequently_accessed(self, limit=10):
        """Get the most frequently accessed files."""
        return sorted(
            [(path, data) for path, data in self.usage_data.items() if os.path.exists(path)],
            key=lambda item: item[1]["access_count"],
            reverse=True
        )[:limit]
    
    def get_infrequently_accessed(self, limit=10):
        """Get the least frequently accessed files."""
        return sorted(
            [(path, data) for path, data in self.usage_data.items() if os.path.exists(path)],
            key=lambda item: item[1]["access_count"]
        )[:limit]
    
    def get_storage_cost(self, cost_per_gb=0.10):
        """Calculate storage cost based on file size and access frequency."""
        total_cost = 0
        for file_path, data in self.usage_data.items():
            try:
                if os.path.exists(file_path):
                    size_gb = os.path.getsize(file_path) / (1024 ** 3)
                    total_cost += size_gb * cost_per_gb
            except (FileNotFoundError, OSError):
                continue
        return total_cost
    
    def cleanup_old_entries(self):
        """Remove entries for files that no longer exist"""
        to_remove = []
        for file_path in self.usage_data:
            if not os.path.exists(file_path):
                to_remove.append(file_path)
        
        for file_path in to_remove:
            del self.usage_data[file_path]
        
        if to_remove:
            self.save_usage_data()
    
    def get_access_statistics(self):
        """Get comprehensive access statistics."""
        total_files = len(self.usage_data)
        accessed_files = len([d for d in self.usage_data.values() if d["access_count"] > 0])
        never_accessed = total_files - accessed_files
        
        if total_files == 0:
            return {
                "total_files": 0,
                "accessed_files": 0,
                "never_accessed": 0,
                "access_rate": 0.0
            }
        
        return {
            "total_files": total_files,
            "accessed_files": accessed_files,
            "never_accessed": never_accessed,
            "access_rate": (accessed_files / total_files) * 100
        }
