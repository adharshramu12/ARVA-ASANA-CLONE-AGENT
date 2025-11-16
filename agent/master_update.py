#!/usr/bin/env python3
"""
Master Update Script - Applies all improvements to the Asana Cloning Agent
Run this after making changes to ensure everything is synchronized
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description, cwd=None):
    """Run a command and report status"""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            shell=True if isinstance(cmd, str) else False
        )
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        if e.stderr:
            print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Run all update steps"""
    print("="*70)
    print("  ASANA CLONING AGENT - MASTER UPDATE")
    print("="*70)
    print("\nThis will update all components and verify the system")
    
    root = Path(__file__).parent.parent
    agent_dir = root / 'agent'
    frontend_dir = root / 'frontend'
    
    results = {}
    
    # Step 1: Verify system
    print("\n🔍 Step 1: Verifying system components...")
    results['verify'] = run_command(
        [sys.executable, 'verify_system.py'],
        "System Verification",
        cwd=agent_dir
    )
    
    # Step 2: Fix SVG attributes in generated files
    print("\n🎨 Step 2: Fixing SVG attributes...")
    results['svg'] = run_command(
        [sys.executable, 'fix_svg_attributes.py'],
        "SVG Attribute Fixes",
        cwd=agent_dir
    )
    
    # Step 3: Apply horizontal scroll (if needed)
    print("\n↔️ Step 3: Applying horizontal scroll...")
    results['scroll'] = run_command(
        [sys.executable, 'apply_horizontal_scroll.py'],
        "Horizontal Scroll Application",
        cwd=agent_dir
    )
    
    # Step 4: Check frontend package.json exists
    print("\n📦 Step 4: Checking frontend dependencies...")
    if (frontend_dir / 'package.json').exists():
        print("✅ package.json found")
        results['deps'] = True
    else:
        print("❌ package.json not found")
        results['deps'] = False
    
    # Step 5: Verify generated components
    print("\n🔍 Step 5: Checking generated components...")
    generated_dir = frontend_dir / 'generated'
    if generated_dir.exists():
        jsx_files = list(generated_dir.glob('*.jsx'))
        if jsx_files:
            print(f"✅ Found {len(jsx_files)} generated components:")
            for f in jsx_files:
                print(f"   - {f.name}")
            results['components'] = True
        else:
            print("⚠️  No generated components found")
            results['components'] = False
    else:
        print("⚠️  Generated directory not found")
        results['components'] = False
    
    # Summary
    print("\n" + "="*70)
    print("  UPDATE SUMMARY")
    print("="*70)
    
    for step, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {step.capitalize()}")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print(f"\n📊 Results: {passed}/{total} steps completed successfully")
    
    if passed == total:
        print("\n🎉 UPDATE COMPLETE!")
        print("\n🚀 Your Asana clone is ready. Next steps:")
        print("   1. cd frontend")
        print("   2. npm install (if not done)")
        print("   3. npm run dev")
        print("   4. Visit http://localhost:3000")
    else:
        print("\n⚠️  Some steps failed. Check the output above for details.")
    
    print("\n" + "="*70)
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
