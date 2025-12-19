#!/usr/bin/env python3
"""
Clean Cache Utility

Removes all __pycache__ folders and *.pyc files recursively from the project.
Run this if imports act weird or you see stale bytecode issues.
"""

import os
import shutil
from pathlib import Path

def clean_pycache(root_dir=None):
    """
    Recursively remove all __pycache__ directories and .pyc files.
    
    Args:
        root_dir: Root directory to clean (defaults to project root)
    """
    if root_dir is None:
        # Assume script is in tools/, so go up one level
        root_dir = Path(__file__).parent.parent
    
    root_path = Path(root_dir).resolve()
    
    removed_dirs = []
    removed_files = []
    
    # Find and remove __pycache__ directories
    for pycache_dir in root_path.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            removed_dirs.append(str(pycache_dir.relative_to(root_path)))
            print(f"Removed: {pycache_dir.relative_to(root_path)}")
        except Exception as e:
            print(f"Error removing {pycache_dir}: {e}")
    
    # Find and remove .pyc files
    for pyc_file in root_path.rglob("*.pyc"):
        try:
            pyc_file.unlink()
            removed_files.append(str(pyc_file.relative_to(root_path)))
            print(f"Removed: {pyc_file.relative_to(root_path)}")
        except Exception as e:
            print(f"Error removing {pyc_file}: {e}")
    
    print(f"\n✅ Cleanup complete!")
    print(f"   Removed {len(removed_dirs)} __pycache__ directories")
    print(f"   Removed {len(removed_files)} .pyc files")

if __name__ == "__main__":
    import sys
    
    # Allow specifying a directory as argument
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = None
    
    print("🧹 Cleaning Python cache files...")
    print("=" * 50)
    clean_pycache(target_dir)

