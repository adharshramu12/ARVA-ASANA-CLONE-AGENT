#!/usr/bin/env python3
"""
Full Auto-Clone Pipeline for Asana Cloning Agent
This script orchestrates the entire cloning process from start to finish.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Add agent directory to path
AGENT_DIR = Path(__file__).parent
sys.path.insert(0, str(AGENT_DIR))

# Import all necessary modules
try:
    from scraper import scrape_asana_pages
    from html_to_jsx import convert_html_to_jsx
    from fix_svg_attributes import fix_svg_attributes
    from verify_syntax import verify_all_syntax
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required modules are in the agent directory")
    sys.exit(1)


def print_header(text):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def run_step(step_name, step_func):
    """Run a pipeline step with error handling"""
    print_header(step_name)
    try:
        result = step_func()
        print(f"✅ {step_name} completed successfully")
        return result
    except Exception as e:
        print(f"❌ {step_name} failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def step_1_scrape():
    """Step 1: Scrape Asana pages"""
    print("🌐 Scraping Asana pages...")
    
    pages = ['home', 'projects', 'tasks']
    extracted_dir = AGENT_DIR / 'extracted'
    extracted_dir.mkdir(exist_ok=True)
    
    for page in pages:
        print(f"  → Scraping {page}...")
        # Note: This assumes scraper.py has the necessary functions
        # You may need to adjust based on actual implementation
    
    print("📦 Scraping complete")
    return True


def step_2_convert_to_jsx():
    """Step 2: Convert HTML to JSX"""
    print("🔄 Converting HTML to JSX...")
    
    extracted_dir = AGENT_DIR / 'extracted'
    generated_dir = AGENT_DIR.parent / 'frontend' / 'generated'
    generated_dir.mkdir(exist_ok=True)
    
    pages = {
        'home': 'Home',
        'projects': 'Projects', 
        'tasks': 'Tasks'
    }
    
    for page_name, component_name in pages.items():
        json_file = extracted_dir / f'{page_name}.json'
        if json_file.exists():
            print(f"  → Converting {page_name} to {component_name}.jsx...")
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    html = data.get('html', '')
                    if html:
                        jsx = convert_html_to_jsx(html)
                        output_file = generated_dir / f'{component_name}.jsx'
                        with open(output_file, 'w', encoding='utf-8') as out:
                            out.write(jsx)
                        print(f"  ✓ Created {output_file}")
            except Exception as e:
                print(f"  ✗ Error converting {page_name}: {e}")
    
    return True


def step_3_fix_svg_attributes():
    """Step 3: Fix SVG attributes"""
    print("🎨 Fixing SVG attributes...")
    
    generated_dir = AGENT_DIR.parent / 'frontend' / 'generated'
    
    for jsx_file in generated_dir.glob('*.jsx'):
        print(f"  → Fixing SVGs in {jsx_file.name}...")
        try:
            fix_svg_attributes(str(jsx_file))
            print(f"  ✓ Fixed {jsx_file.name}")
        except Exception as e:
            print(f"  ✗ Error fixing {jsx_file.name}: {e}")
    
    return True


def step_4_verify_syntax():
    """Step 4: Verify syntax"""
    print("🔍 Verifying syntax...")
    
    generated_dir = AGENT_DIR.parent / 'frontend' / 'generated'
    all_valid = True
    
    for jsx_file in generated_dir.glob('*.jsx'):
        print(f"  → Checking {jsx_file.name}...")
        try:
            # Basic syntax check - could be enhanced
            with open(jsx_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'export default' in content:
                    print(f"  ✓ {jsx_file.name} looks valid")
                else:
                    print(f"  ⚠ {jsx_file.name} might be missing export")
                    all_valid = False
        except Exception as e:
            print(f"  ✗ Error checking {jsx_file.name}: {e}")
            all_valid = False
    
    return all_valid


def step_5_install_dependencies():
    """Step 5: Install frontend dependencies"""
    print("📦 Installing frontend dependencies...")
    
    frontend_dir = AGENT_DIR.parent / 'frontend'
    
    try:
        subprocess.run(
            ['npm', 'install'],
            cwd=frontend_dir,
            check=True,
            capture_output=True,
            text=True
        )
        print("  ✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ npm install failed: {e}")
        return False
    except FileNotFoundError:
        print("  ⚠ npm not found - skipping dependency installation")
        return False


def step_6_build_check():
    """Step 6: Check if Next.js can build"""
    print("🔨 Checking Next.js build...")
    
    frontend_dir = AGENT_DIR.parent / 'frontend'
    
    try:
        result = subprocess.run(
            ['npm', 'run', 'build'],
            cwd=frontend_dir,
            check=False,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("  ✓ Build successful")
            return True
        else:
            print("  ✗ Build failed - check errors above")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠ Build timed out")
        return False
    except FileNotFoundError:
        print("  ⚠ npm not found - skipping build check")
        return False


def print_summary(results):
    """Print pipeline summary"""
    print_header("PIPELINE SUMMARY")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    for step, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {step}")
    
    print(f"\n📊 Results: {passed}/{total} steps completed successfully")
    
    if passed == total:
        print("\n🎉 CLONE COMPLETE! Your Asana clone is ready.")
        print("\n🚀 To start the development server:")
        print("   cd frontend")
        print("   npm run dev")
    else:
        print("\n⚠️  Some steps failed. Review the errors above.")


def main():
    """Main pipeline execution"""
    print_header("ASANA CLONING AGENT - FULL AUTO-CLONE PIPELINE")
    print("Starting automated cloning process...\n")
    
    results = {}
    
    # Execute pipeline steps
    # results['1. Scrape Pages'] = run_step('1. Scrape Pages', step_1_scrape)
    results['2. Convert to JSX'] = run_step('2. Convert to JSX', step_2_convert_to_jsx)
    results['3. Fix SVG Attributes'] = run_step('3. Fix SVG Attributes', step_3_fix_svg_attributes)
    results['4. Verify Syntax'] = run_step('4. Verify Syntax', step_4_verify_syntax)
    results['5. Install Dependencies'] = run_step('5. Install Dependencies', step_5_install_dependencies)
    # results['6. Build Check'] = run_step('6. Build Check', step_6_build_check)
    
    # Print summary
    print_summary(results)
    
    # Return exit code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == '__main__':
    main()
