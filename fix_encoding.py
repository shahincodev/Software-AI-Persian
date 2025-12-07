#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix encoding corruption in markdown files
Converts incorrectly encoded Persian text back to proper UTF-8
"""

import os
import glob
from pathlib import Path

def fix_file_encoding(file_path):
    """Fix encoding of a single file"""
    try:
        # Try reading with various encodings
        content = None
        
        # First try UTF-8
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            pass
        
        # If that fails, try with cp1252 (Windows default)
        if content is None:
            try:
                with open(file_path, 'r', encoding='cp1252') as f:
                    content = f.read()
            except:
                pass
        
        # If still fails, try latin-1
        if content is None:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except:
                return False
        
        # Now write back with proper UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        print(f"✅ Fixed: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all markdown files in docs directory"""
    docs_dir = Path(__file__).parent / "docs"
    
    if not docs_dir.exists():
        print(f"❌ Directory not found: {docs_dir}")
        return
    
    # Get all markdown files
    md_files = list(docs_dir.glob("*.md"))
    
    print(f"🔍 Found {len(md_files)} markdown files")
    print("="*50)
    
    fixed_count = 0
    failed_count = 0
    
    for md_file in md_files:
        if fix_file_encoding(md_file):
            fixed_count += 1
        else:
            failed_count += 1
    
    print("="*50)
    print(f"\n📊 Summary:")
    print(f"✅ Fixed: {fixed_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📁 Total: {len(md_files)}")

if __name__ == "__main__":
    main()
