#!/usr/bin/env python3
"""Verify JSX syntax"""

import os
import re

def verify_syntax(file_path):
    """Verify the JSX file has correct syntax"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if template literal is properly closed
    pattern = r'const htmlContent = sanitizeHtml\(`([^`]*)`\);'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        print(f"[SUCCESS] Template literal properly closed in {os.path.basename(file_path)}")
        html_length = len(match.group(1))
        print(f"[INFO] HTML content length: {html_length} characters")
        return True
    else:
        print(f"[ERROR] Template literal NOT properly closed in {os.path.basename(file_path)}")
        # Try to find where it breaks
        start = content.find('const htmlContent = sanitizeHtml(')
        if start >= 0:
            # Look for the end
            end1 = content.find('`);', start)
            end2 = content.find('`;', start)
            print(f"[DEBUG] Found '`);' at: {end1}")
            print(f"[DEBUG] Found '`;' at: {end2}")
            if end1 < 0 and end2 >= 0:
                print("[ERROR] Template literal ends with `; instead of `);")
        return False

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    files = [
        os.path.join(script_dir, "..", "frontend", "generated", "Home.jsx"),
        os.path.join(script_dir, "..", "frontend", "generated", "Projects.jsx"),
        os.path.join(script_dir, "..", "frontend", "generated", "Tasks.jsx"),
    ]
    
    for file_path in files:
        print(f"\n[INFO] Checking {os.path.basename(file_path)}...")
        verify_syntax(file_path)

