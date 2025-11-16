import re

def fix_home_jsx():
    """Fix syntax errors in Home.jsx"""
    print("[INFO] Reading Home.jsx...")
    with open("frontend/generated/Home.jsx", "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.split('\n')
    print(f"[INFO] Total lines: {len(lines)}")
    
    # Find the problematic line 13 (index 12)
    if len(lines) > 12:
        line_13 = lines[12]
        print(f"[INFO] Line 13 length: {len(line_13)} characters")
        
        # Fix common issues:
        # 1. Fix link tag to be self-closing
        line_13 = re.sub(r'<link([^>]*?)(?<!/)>', r'<link\1 />', line_13)
        
        # 2. Fix any ><div issues (should be just <div)
        line_13 = re.sub(r'><div', r'<div', line_13)
        
        # 3. Ensure all iframes are self-closing or properly closed
        line_13 = re.sub(r'<iframe([^>]*?)(?<!/)>', r'<iframe\1 />', line_13)
        
        # 4. Check for unclosed main tag - find and fix
        # Count opening and closing main tags
        main_open = line_13.count('<main')
        main_close = line_13.count('</main>')
        
        if main_open > main_close:
            # Find the last opening main tag and ensure it's closed
            last_main_pos = line_13.rfind('<main')
            if last_main_pos != -1:
                # Check if there's a closing main after this
                remaining = line_13[last_main_pos:]
                if '</main>' not in remaining:
                    # Add closing main before the closing div
                    line_13 = line_13.replace('</div></div></div></div>', '</main></div></div></div></div>', 1)
                    print("[INFO] Fixed unclosed main tag")
        
        # 5. Ensure proper closing of all divs
        # Count opening and closing divs
        div_open = line_13.count('<div')
        div_close = line_13.count('</div>')
        
        # Count self-closing divs
        self_closing_divs = line_13.count('<div[^>]*/>')
        
        # Adjust count
        actual_open = div_open - self_closing_divs
        
        if actual_open > div_close:
            missing = actual_open - div_close
            print(f"[WARN] Missing {missing} closing div tags")
            # Add missing closing divs before the last closing div of the wrapper
            line_13 = line_13.replace('    </div>', '</div>' * missing + '    </div>', 1)
        
        lines[12] = line_13
    
    # Write back
    fixed_content = '\n'.join(lines)
    
    with open("frontend/generated/Home.jsx", "w", encoding="utf-8") as f:
        f.write(fixed_content)
    
    print("[SUCCESS] Home.jsx fixed!")

if __name__ == "__main__":
    fix_home_jsx()

