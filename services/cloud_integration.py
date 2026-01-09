import os
from pathlib import Path

def list_local_files(directory):
    """List all files in a local directory recursively"""
    files = []
    for root, _, filenames in os.walk(directory):
        for fname in filenames:
            files.append(str(Path(root) / fname))
    return files

def list_cloud_files(cloud_dir):
    """Stub: List files in a cloud directory (simulate for now)"""
    # In a real implementation, integrate with cloud SDKs (e.g., Google Drive, Dropbox)
    # Here, just simulate with a local path for demonstration
    return list_local_files(cloud_dir)

def compare_files(local_files, cloud_files):
    """Compare local and cloud files by name and size"""
    local_set = set((Path(f).name, os.path.getsize(f)) for f in local_files if os.path.exists(f))
    cloud_set = set((Path(f).name, os.path.getsize(f)) for f in cloud_files if os.path.exists(f))
    only_local = local_set - cloud_set
    only_cloud = cloud_set - local_set
    both = local_set & cloud_set
    return {
        "only_local": only_local,
        "only_cloud": only_cloud,
        "both": both
    }

def suggest_migration(only_local, threshold_size=10*1024*1024):
    """Suggest files for migration to cloud (e.g., large files only)"""
    return [f for f in only_local if f[1] >= threshold_size]
