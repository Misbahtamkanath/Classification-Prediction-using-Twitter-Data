#!/usr/bin/env python3
"""Script to rename classification prediction folder"""

from pathlib import Path
import os
import sys

def main():
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        src = Path('classification prediction')
        dst = Path('classification_prediction')
        
        print(f"Current directory: {os.getcwd()}")
        print(f"Looking for: {src}")
        print(f"Source exists: {src.exists()}")
        print(f"Destination exists: {dst.exists()}")
        
        if src.exists() and not dst.exists():
            src.rename(dst)
            print("✅ Successfully renamed 'classification prediction' -> 'classification_prediction'")
            return 0
        elif dst.exists():
            print("⚠️  Destination already exists, skipping rename")
            return 0
        else:
            print("❌ Source folder not found")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
