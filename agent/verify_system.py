#!/usr/bin/env python3
"""
Verification script to check all components are properly set up
"""

import os
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status"""
    if os.path.exists(file_path):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - FILE NOT FOUND: {file_path}")
        return False

def check_file_contains(file_path, search_string, description):
    """Check if a file contains a specific string"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - String not found")
                return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def main():
    """Run all verification checks"""
    print("="*70)
    print("  ASANA CLONING AGENT - SYSTEM VERIFICATION")
    print("="*70)
    
    root = Path(__file__).parent.parent
    frontend = root / 'frontend'
    agent = root / 'agent'
    
    checks = []
    
    print("\n📁 Checking Frontend Components...")
    checks.append(check_file_exists(
        frontend / 'components' / 'HorizontalDragScroll.tsx',
        "HorizontalDragScroll component"
    ))
    checks.append(check_file_exists(
        frontend / 'components' / 'DropdownManager.tsx',
        "DropdownManager component"
    ))
    checks.append(check_file_exists(
        frontend / 'components' / 'LinkInterceptor.tsx',
        "LinkInterceptor component"
    ))
    
    print("\n🎨 Checking Styling...")
    checks.append(check_file_contains(
        frontend / 'app' / 'globals.css',
        'no-scrollbar',
        "No-scrollbar CSS class"
    ))
    checks.append(check_file_contains(
        frontend / 'app' / 'globals.css',
        'horizontal-scroll-container',
        "Horizontal scroll CSS class"
    ))
    
    print("\n🔧 Checking Configuration...")
    checks.append(check_file_contains(
        frontend / 'app' / 'layout.tsx',
        'DropdownProvider',
        "DropdownProvider in layout"
    ))
    checks.append(check_file_contains(
        frontend / 'app' / 'layout.tsx',
        'LinkInterceptor',
        "LinkInterceptor in layout"
    ))
    checks.append(check_file_contains(
        frontend / 'app' / 'layout.tsx',
        '#F7F7F7',
        "Asana background color"
    ))
    
    print("\n🛠️ Checking Sanitizer...")
    checks.append(check_file_contains(
        frontend / 'lib' / 'sanitizeHtml.ts',
        'ass="',
        "Garbage text removal"
    ))
    checks.append(check_file_contains(
        frontend / 'lib' / 'sanitizeHtml.ts',
        'ThemeableCardPresentation',
        "Problematic class removal"
    ))
    checks.append(check_file_contains(
        frontend / 'lib' / 'sanitizeHtml.ts',
        'overlay',
        "Overlay removal"
    ))
    
    print("\n🐍 Checking Agent Scripts...")
    checks.append(check_file_exists(
        agent / 'run_full_clone.py',
        "Full auto-clone pipeline"
    ))
    checks.append(check_file_exists(
        agent / 'apply_horizontal_scroll.py',
        "Horizontal scroll applicator"
    ))
    checks.append(check_file_exists(
        agent / 'fix_svg_attributes.py',
        "SVG attribute fixer"
    ))
    
    print("\n📚 Checking Documentation...")
    checks.append(check_file_exists(
        root / 'README-COMPLETE.md',
        "Complete documentation"
    ))
    checks.append(check_file_exists(
        root / 'QUICK-START.md',
        "Quick start guide"
    ))
    
    print("\n" + "="*70)
    print("  VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n✅ Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! System is ready to use.")
        print("\n🚀 Next steps:")
        print("   1. cd frontend && npm install")
        print("   2. npm run dev")
        print("   3. Visit http://localhost:3000")
    else:
        print(f"\n⚠️  {total - passed} checks failed. Review the errors above.")
    
    print("\n" + "="*70)
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    exit(main())
