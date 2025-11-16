import os
import re

def fix_home_datatestid():
    """Fix dataTestid in Home.jsx HTML content"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "..", "frontend", "generated", "Home.jsx")
    
    print(f"[INFO] Reading {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the HTML content in the template literal
    html_match = re.search(r'const htmlContent = `([^`]*)`;', content, re.DOTALL)
    
    if not html_match:
        print("[ERROR] Could not find htmlContent template literal")
        return
    
    html_content = html_match.group(1)
    print(f"[INFO] Found HTML content: {len(html_content)} characters")
    
    # Count occurrences before fixing
    count_before = len(re.findall(r'dataTestid=', html_content))
    print(f"[INFO] Found {count_before} occurrences of 'dataTestid'")
    
    if count_before > 0:
        # Fix dataTestid to data-testid in HTML content
        html_content = re.sub(r'dataTestid=', 'data-testid=', html_content)
        
        # Replace the HTML content in the file
        new_content = content[:html_match.start(1)] + html_content + content[html_match.end(1):]
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        count_after = len(re.findall(r'dataTestid=', html_content))
        print(f"[SUCCESS] Fixed {count_before} occurrences of 'dataTestid' -> 'data-testid'")
        print(f"[INFO] Remaining: {count_after} occurrences")
    else:
        print("[INFO] No 'dataTestid' found, already correct")

if __name__ == "__main__":
    fix_home_datatestid()

