import os
import re

def verify_all_components():
    """Verify all components follow Fast Refresh rules"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=== VERIFYING FAST REFRESH COMPATIBILITY ===\n")
    
    components_dir = os.path.join(script_dir, '..', 'frontend', 'components')
    generated_dir = os.path.join(script_dir, '..', 'frontend', 'generated')
    
    issues = []
    
    # Check all component files
    for directory in [components_dir, generated_dir]:
        if not os.path.exists(directory):
            continue
        
        for filename in os.listdir(directory):
            if not filename.endswith('.jsx'):
                continue
            
            file_path = os.path.join(directory, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Fast Refresh requirements
            # 1. Must have default export
            if 'export default' not in content:
                issues.append(f"{filename}: Missing default export")
            
            # 2. Named exports must be supported (not checked for now)
            
            # 3. Check for dataTestid (should be data-testid)
            if 'dataTestid=' in content:
                count = len(re.findall(r'dataTestid=', content))
                issues.append(f"{filename}: Has {count} occurrences of 'dataTestid' (should be 'data-testid')")
            
            # 4. Check if client component has 'use client'
            uses_client_features = any([
                'tabIndex' in content,
                'onClick' in content,
                'onChange' in content,
                'useState' in content,
                'useEffect' in content,
                'addEventListener' in content,
                'role="button"' in content,
            ])
            
            has_use_client = "'use client'" in content or '"use client"' in content
            
            if uses_client_features and not has_use_client:
                issues.append(f"{filename}: Uses client features but missing 'use client' directive")
    
    if issues:
        print("❌ Issues found:\n")
        for issue in issues:
            print(f"  • {issue}")
        print()
    else:
        print("✅ All components follow Fast Refresh rules!\n")
    
    return len(issues) == 0

if __name__ == "__main__":
    verify_all_components()

