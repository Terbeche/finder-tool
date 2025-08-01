import os
import time
import threading
from collections import defaultdict
from pathlib import Path
from datetime import datetime
import psutil

class PerformanceOptimizer:
    """Optimizes application performance and monitors system resources"""
    
    def __init__(self):
        self.scan_cache = {}
        self.file_cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.max_cache_size = 1000
        self.performance_stats = {
            "scan_times": [],
            "memory_usage": [],
            "cpu_usage": [],
            "cache_hits": 0,
            "cache_misses": 0
        }
        self.monitoring_enabled = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start performance monitoring"""
        if not self.monitoring_enabled:
            self.monitoring_enabled = True
            self.monitor_thread = threading.Thread(target=self._monitor_performance, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_enabled = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_performance(self):
        """Monitor system performance in background"""
        while self.monitoring_enabled:
            try:
                # Monitor memory usage
                process = psutil.Process()
                memory_info = process.memory_info()
                self.performance_stats["memory_usage"].append({
                    "timestamp": time.time(),
                    "rss": memory_info.rss,
                    "vms": memory_info.vms
                })
                
                # Monitor CPU usage
                cpu_percent = process.cpu_percent()
                self.performance_stats["cpu_usage"].append({
                    "timestamp": time.time(),
                    "cpu_percent": cpu_percent
                })
                
                # Limit stats history
                if len(self.performance_stats["memory_usage"]) > 100:
                    self.performance_stats["memory_usage"] = self.performance_stats["memory_usage"][-50:]
                if len(self.performance_stats["cpu_usage"]) > 100:
                    self.performance_stats["cpu_usage"] = self.performance_stats["cpu_usage"][-50:]
                
                time.sleep(5)  # Monitor every 5 seconds
            except Exception:
                break
    
    def cache_directory_scan(self, directory, file_count, scan_time):
        """Cache directory scan results"""
        cache_key = str(Path(directory).resolve())
        self.scan_cache[cache_key] = {
            "file_count": file_count,
            "scan_time": scan_time,
            "timestamp": time.time(),
            "directory_mtime": os.path.getmtime(directory)
        }
        
        # Limit cache size
        if len(self.scan_cache) > self.max_cache_size:
            oldest_key = min(self.scan_cache.keys(), 
                           key=lambda k: self.scan_cache[k]["timestamp"])
            del self.scan_cache[oldest_key]
    
    def get_cached_scan(self, directory):
        """Get cached scan results if valid"""
        cache_key = str(Path(directory).resolve())
        
        if cache_key not in self.scan_cache:
            self.performance_stats["cache_misses"] += 1
            return None
        
        cached = self.scan_cache[cache_key]
        
        # Check if cache is expired
        if time.time() - cached["timestamp"] > self.cache_timeout:
            del self.scan_cache[cache_key]
            self.performance_stats["cache_misses"] += 1
            return None
        
        # Check if directory was modified
        try:
            current_mtime = os.path.getmtime(directory)
            if current_mtime > cached["directory_mtime"]:
                del self.scan_cache[cache_key]
                self.performance_stats["cache_misses"] += 1
                return None
        except OSError:
            del self.scan_cache[cache_key]
            self.performance_stats["cache_misses"] += 1
            return None
        
        self.performance_stats["cache_hits"] += 1
        return cached
    
    def optimize_scan_strategy(self, directory, file_count_estimate=None):
        """Determine optimal scanning strategy based on directory size"""
        if not os.path.exists(directory):
            return {"strategy": "normal", "batch_size": 1000}
        
        # Quick estimate of directory size
        if file_count_estimate is None:
            try:
                # Sample first few items to estimate
                items = list(Path(directory).iterdir())[:100]
                subdirs = sum(1 for item in items if item.is_dir())
                files = len(items) - subdirs
                
                # Rough estimate
                if subdirs > 50:
                    file_count_estimate = files * 50  # Assume many subdirectories
                else:
                    file_count_estimate = files * 5
            except (OSError, PermissionError):
                file_count_estimate = 1000
        
        # Determine strategy
        if file_count_estimate < 1000:
            return {"strategy": "fast", "batch_size": 100}
        elif file_count_estimate < 10000:
            return {"strategy": "normal", "batch_size": 500}
        else:
            return {"strategy": "conservative", "batch_size": 1000}
    
    def record_scan_performance(self, directory, file_count, scan_time):
        """Record scan performance metrics"""
        self.performance_stats["scan_times"].append({
            "directory": directory,
            "file_count": file_count,
            "scan_time": scan_time,
            "timestamp": time.time()
        })
        
        # Cache the results
        self.cache_directory_scan(directory, file_count, scan_time)
        
        # Limit history
        if len(self.performance_stats["scan_times"]) > 50:
            self.performance_stats["scan_times"] = self.performance_stats["scan_times"][-25:]
    
    def get_performance_report(self):
        """Generate performance report"""
        report = {
            "cache_efficiency": self._calculate_cache_efficiency(),
            "average_scan_time": self._calculate_average_scan_time(),
            "memory_usage": self._get_memory_summary(),
            "cpu_usage": self._get_cpu_summary(),
            "recommendations": self._generate_recommendations()
        }
        return report
    
    def _calculate_cache_efficiency(self):
        """Calculate cache hit ratio"""
        total_requests = self.performance_stats["cache_hits"] + self.performance_stats["cache_misses"]
        if total_requests == 0:
            return 0.0
        return (self.performance_stats["cache_hits"] / total_requests) * 100
    
    def _calculate_average_scan_time(self):
        """Calculate average scan time per file"""
        scan_times = self.performance_stats["scan_times"]
        if not scan_times:
            return 0.0
        
        total_time = sum(s["scan_time"] for s in scan_times)
        total_files = sum(s["file_count"] for s in scan_times)
        
        if total_files == 0:
            return 0.0
        
        return total_time / total_files
    
    def _get_memory_summary(self):
        """Get memory usage summary"""
        memory_data = self.performance_stats["memory_usage"]
        if not memory_data:
            return {"current": 0, "peak": 0, "average": 0}
        
        current = memory_data[-1]["rss"] if memory_data else 0
        peak = max(m["rss"] for m in memory_data)
        average = sum(m["rss"] for m in memory_data) / len(memory_data)
        
        return {
            "current": current / (1024 * 1024),  # MB
            "peak": peak / (1024 * 1024),       # MB
            "average": average / (1024 * 1024)  # MB
        }
    
    def _get_cpu_summary(self):
        """Get CPU usage summary"""
        cpu_data = self.performance_stats["cpu_usage"]
        if not cpu_data:
            return {"current": 0, "peak": 0, "average": 0}
        
        current = cpu_data[-1]["cpu_percent"] if cpu_data else 0
        peak = max(c["cpu_percent"] for c in cpu_data)
        average = sum(c["cpu_percent"] for c in cpu_data) / len(cpu_data)
        
        return {
            "current": current,
            "peak": peak,
            "average": average
        }
    
    def _generate_recommendations(self):
        """Generate performance recommendations"""
        recommendations = []
        
        # Cache efficiency
        cache_efficiency = self._calculate_cache_efficiency()
        if cache_efficiency < 50:
            recommendations.append("Consider increasing cache timeout for better performance")
        
        # Memory usage
        memory_summary = self._get_memory_summary()
        if memory_summary["peak"] > 500:  # 500MB
            recommendations.append("High memory usage detected - consider scanning smaller directories")
        
        # CPU usage
        cpu_summary = self._get_cpu_summary()
        if cpu_summary["average"] > 80:
            recommendations.append("High CPU usage - consider reducing scan depth or using filters")
        
        # Scan times
        avg_time = self._calculate_average_scan_time()
        if avg_time > 0.001:  # 1ms per file
            recommendations.append("Slow scanning detected - check disk performance or reduce file count")
        
        if not recommendations:
            recommendations.append("Performance is optimal")
        
        return recommendations
    
    def clear_cache(self):
        """Clear all caches"""
        self.scan_cache.clear()
        self.file_cache.clear()
        self.performance_stats["cache_hits"] = 0
        self.performance_stats["cache_misses"] = 0
    
    def optimize_memory_usage(self):
        """Perform memory optimization"""
        import gc
        
        # Clear caches if memory usage is high
        memory_summary = self._get_memory_summary()
        if memory_summary["current"] > 300:  # 300MB
            # Clear older cache entries
            current_time = time.time()
            expired_keys = [
                k for k, v in self.scan_cache.items()
                if current_time - v["timestamp"] > self.cache_timeout / 2
            ]
            for key in expired_keys:
                del self.scan_cache[key]
        
        # Force garbage collection
        gc.collect()
        
        return len(expired_keys) if 'expired_keys' in locals() else 0
