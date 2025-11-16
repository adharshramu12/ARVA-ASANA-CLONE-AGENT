#!/usr/bin/env python3
"""Check template literal for syntax issues"""

import os
import re

def check_template_literal(file_path):
    """Check if template literal has syntax issues"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the template literal
    start = content.find('const htmlContent = sanitizeHtml(')
    if start < 0:
        print(f"[ERROR] Could not find sanitizeHtml call in {file_path}")
        return False
    
    # Find the end of template literal
    end = content.find('`);', start)
    if end < 0:
        print(f"[ERROR] Could not find end of template literal in {file_path}")
        return False
    
    html = content[start+34:end]  # +34 for 'const htmlContent = sanitizeHtml('
    
    # Check for unescaped backticks
    backticks = html.count('`')
    if backticks > 0:
        print(f"[WARN] Found {backticks} backticks in HTML content")
        # Find positions
        for i, char in enumerate(html):
            if char == '`':
                print(f"  Backtick at position {i}: {repr(html[max(0, i-20):i+20])}")
    
    # Check for template expressions
    template_exprs = len(re.findall(r'\$\{', html))
    if template_exprs > 0:
        print(f"[WARN] Found {template_exprs} template expressions in HTML")
    
    # Check for common issues
    if html.startswith('<link'):
        print("[INFO] HTML starts with <link tag (OK)")
    else:
        print(f"[WARN] HTML doesn't start with <link: {repr(html[:50])}")
    
    if html.endswith(' />`'):
        print("[INFO] HTML ends correctly")
    else:
        print(f"[WARN] HTML doesn't end correctly: {repr(html[-50:])}")
    
    return True

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "..", "frontend", "generated", "Home.jsx")
    check_template_literal(file_path)

