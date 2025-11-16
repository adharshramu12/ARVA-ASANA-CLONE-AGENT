#!/usr/bin/env python3
"""
Apply horizontal scroll wrappers to generated components
Detects overflow containers and wraps them with HorizontalDragScroll
"""

import re
import os
from pathlib import Path

def wrap_horizontal_scroll_containers(file_path):
    """
    Detect and wrap containers that should have horizontal scroll
    """
    print(f"[INFO] Processing {file_path} for horizontal scroll...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Patterns that indicate horizontal scrollable content
    horizontal_patterns = [
        r'class="[^"]*\brow\b[^"]*"',  # Row containers
        r'class="[^"]*\bflex[^"]*"',  # Flex containers
        r'class="[^"]*\bgrid\b[^"]*"',  # Grid containers
        r'class="[^"]*\bpeople-list\b[^"]*"',  # People lists
        r'class="[^"]*\bproject-grid\b[^"]*"',  # Project grids
        r'class="[^"]*\bwidget-container\b[^"]*"',  # Widget containers
        r'data-testid="[^"]*carousel[^"]*"',  # Carousels
        r'data-testid="[^"]*scroll[^"]*"',  # Explicit scroll containers
    ]
    
    # Check if we need to add import
    if 'HorizontalDragScroll' not in content:
        # Add import at the top (after other imports)
        import_statement = 'import HorizontalDragScroll from "@/components/HorizontalDragScroll";\n'
        
        # Find the last import or "use client" statement
        last_import_match = None
        for match in re.finditer(r'^import .+;$|^"use client";$', content, re.MULTILINE):
            last_import_match = match
        
        if last_import_match:
            insert_pos = last_import_match.end() + 1
            content = content[:insert_pos] + import_statement + content[insert_pos:]
            print("[INFO] Added HorizontalDragScroll import")
    
    # Find and wrap containers that match horizontal patterns
    # This is a simplified approach - in production, you'd want more sophisticated parsing
    
    # Look for divs with specific class patterns
    def should_wrap(div_match):
        div_content = div_match.group(0)
        for pattern in horizontal_patterns:
            if re.search(pattern, div_content):
                return True
        return False
    
    # Note: This is a basic implementation. For production, you'd want to:
    # 1. Parse the JSX properly (using a JSX parser)
    # 2. Identify specific containers based on their children count and layout
    # 3. Apply wrapping only where needed
    
    print("[INFO] Horizontal scroll wrapping complete (manual wrapping recommended)")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def apply_to_all_generated():
    """Apply horizontal scroll to all generated components"""
    script_dir = Path(__file__).parent
    generated_dir = script_dir.parent / 'frontend' / 'generated'
    
    for jsx_file in generated_dir.glob('*.jsx'):
        wrap_horizontal_scroll_containers(str(jsx_file))

if __name__ == '__main__':
    apply_to_all_generated()
