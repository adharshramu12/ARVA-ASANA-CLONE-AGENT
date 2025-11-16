import os
import re

def fix_client_directives():
    """Fix Next.js App Router and Fast Refresh issues"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Components that need 'use client' (interactive/client-side features)
    client_components = [
        {
            'path': os.path.join(script_dir, '..', 'frontend', 'components', 'Topbar.jsx'),
            'reason': 'Contains interactive elements (buttons, tabIndex)'
        },
        {
            'path': os.path.join(script_dir, '..', 'frontend', 'components', 'ModalManager.jsx'),
            'reason': 'Modal manager likely needs client-side state'
        },
        {
            'path': os.path.join(script_dir, '..', 'frontend', 'components', 'ToastManager.jsx'),
            'reason': 'Toast manager likely needs client-side state'
        },
        {
            'path': os.path.join(script_dir, '..', 'frontend', 'generated', 'Projects.jsx'),
            'reason': 'Component may need client-side features'
        },
    ]
    
    print("=== FIXING NEXT.JS APP ROUTER & FAST REFRESH ISSUES ===\n")
    
    for comp in client_components:
        if not os.path.exists(comp['path']):
            continue
        
        filename = os.path.basename(comp['path'])
        print(f"Checking {filename}...")
        
        with open(comp['path'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if 'use client' is missing
        has_use_client = "'use client'" in content or '"use client"' in content
        
        # Check if component uses client-side features
        uses_client_features = any([
            'tabIndex' in content,
            'role="button"' in content,
            'onClick' in content,
            'onChange' in content,
            'useState' in content,
            'useEffect' in content,
            'useCallback' in content,
            'useRef' in content,
            'addEventListener' in content,
        ])
        
        if not has_use_client and uses_client_features:
            print(f"  ❌ Missing 'use client' directive ({comp['reason']})")
            
            # Add 'use client' at the top
            if content.startswith("'use client'"):
                print(f"  ⚠️  Already has 'use client'")
            elif content.startswith('"use client"'):
                print(f"  ⚠️  Already has 'use client'")
            elif content.startswith('import '):
                # Add before first import
                lines = content.split('\n')
                content = "'use client';\n\n" + content
            else:
                # Add at the very beginning
                content = "'use client';\n\n" + content
            
            with open(comp['path'], 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ Added 'use client' directive")
        elif has_use_client:
            print(f"  ✅ Already has 'use client' directive")
        else:
            print(f"  ⚪ No client features detected, 'use client' not needed")
        
        print()

def fix_import_issues():
    """Fix import/export issues that cause Fast Refresh problems"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=== CHECKING IMPORT/EXPORT ISSUES ===\n")
    
    # Check page.tsx
    page_path = os.path.join(script_dir, '..', 'frontend', 'app', 'page.tsx')
    if os.path.exists(page_path):
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if Home.jsx export is default
        if 'import HomeUI from' in content:
            # Verify the export
            home_path = os.path.join(script_dir, '..', 'frontend', 'generated', 'Home.jsx')
            if os.path.exists(home_path):
                with open(home_path, 'r', encoding='utf-8') as f:
                    home_content = f.read()
                
                if 'export default function HomeUI' in home_content:
                    print("✅ page.tsx imports HomeUI correctly")
                else:
                    print("❌ Home.jsx doesn't export HomeUI as default")
                    # Fix export
                    if 'export default' in home_content:
                        # Already has export default, might be named differently
                        print("  ⚠️  Checking export name...")
                    else:
                        # Add export default
                        if 'function HomeUI' in home_content:
                            home_content = re.sub(
                                r'function HomeUI\(\)',
                                'export default function HomeUI()',
                                home_content
                            )
                            with open(home_path, 'w', encoding='utf-8') as f:
                                f.write(home_content)
                            print("  ✅ Fixed export")
    
    print()

if __name__ == "__main__":
    fix_client_directives()
    fix_import_issues()
    print("=== DONE ===")

