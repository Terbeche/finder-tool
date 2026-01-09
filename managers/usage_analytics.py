from datetime import datetime
from typing import Dict, Any, List, Tuple
import os

class UsageAnalytics:
    """Tracks file usage and provides analytics"""
    
    def __init__(self):
        self.usage_data = {}
        self.storage_cost_rate = 0.10  # $ per GB per month
    
    def record_access(self, file_path: str):
        """Record file access event"""
        if not file_path or not os.path.exists(file_path):
            return
        
        if file_path not in self.usage_data:
            self.usage_data[file_path] = {
                "access_count": 0,
                "first_accessed": None,
                "last_accessed": None
            }
        
        self.usage_data[file_path]["access_count"] += 1
        
        now = datetime.now().isoformat()
        if not self.usage_data[file_path]["first_accessed"]:
            self.usage_data[file_path]["first_accessed"] = now
        
        self.usage_data[file_path]["last_accessed"] = now
    
    def get_frequently_accessed(self, limit: int = 10) -> List[Tuple[str, Dict[str, Any]]]:
        """Get most frequently accessed files"""
        sorted_items = sorted(
            self.usage_data.items(), 
            key=lambda x: x[1]["access_count"], 
            reverse=True
        )
        return sorted_items[:limit]
    
    def get_rarely_accessed(self, limit: int = 10) -> List[Tuple[str, Dict[str, Any]]]:
        """Get rarely accessed files"""
        sorted_items = sorted(
            self.usage_data.items(), 
            key=lambda x: x[1]["access_count"]
        )
        return sorted_items[:limit]
    
    def get_never_accessed(self) -> List[str]:
        """Get list of files never accessed (not in usage_data)"""
        return [path for path in self.usage_data if self.usage_data[path]["access_count"] == 0]
    
    def get_storage_cost(self, files=None) -> float:
        """Calculate monthly storage cost based on file sizes"""
        if not files:
            return 0.0
        
        total_size_gb = sum(f.size for f in files) / (1024 * 1024 * 1024)
        return total_size_gb * self.storage_cost_rate
    
    def get_access_statistics(self) -> Dict[str, Any]:
        """Get overall access statistics"""
        total_files = len(self.usage_data)
        accessed_files = sum(1 for data in self.usage_data.values() if data["access_count"] > 0)
        never_accessed = total_files - accessed_files
        access_rate = (accessed_files / total_files * 100) if total_files > 0 else 0
        
        return {
            "total_files": total_files,
            "accessed_files": accessed_files,
            "never_accessed": never_accessed,
            "access_rate": access_rate
        }
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
