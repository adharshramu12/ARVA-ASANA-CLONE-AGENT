#!/usr/bin/env python3
"""
Automated Test Runner for Asana Cloning Agent
Runs all tests and opens web preview
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def run_command(cmd, description, cwd=None, shell=False):
    """Run command and return success status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=shell,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print(result.stdout[:500])  # First 500 chars
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        if e.stderr:
            print(e.stderr[:500])
        return False
    except FileNotFoundError:
        print(f"⚠️  {description} - Command not found")
        return False

def check_port_available(port=3000):
    """Check if port is available"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def main():
    """Main test runner"""
    print_header("ASANA CLONING AGENT - AUTOMATED TEST & PREVIEW")
    
    root = Path(__file__).parent
    frontend = root / 'frontend'
    agent = root / 'agent'
    
    results = {}
    
    # Step 1: System Verification
    print_header("STEP 1: System Verification")
    results['verify'] = run_command(
        [sys.executable, 'verify_system.py'],
        "System Verification",
        cwd=agent
    )
    
    # Step 2: Run Full Clone Pipeline
    print_header("STEP 2: Full Clone Pipeline")
    results['pipeline'] = run_command(
        [sys.executable, 'run_full_clone.py'],
        "Full Clone Pipeline",
        cwd=agent
    )
    
    # Step 3: Install Dependencies
    print_header("STEP 3: Installing Dependencies")
    if (frontend / 'node_modules').exists():
        print("✅ Dependencies already installed")
        results['install'] = True
    else:
        results['install'] = run_command(
            ['npm', 'install'],
            "npm install",
            cwd=frontend,
            shell=True
        )
    
    # Step 4: Build Check
    print_header("STEP 4: Build Verification")
    results['build'] = run_command(
        ['npm', 'run', 'build'],
        "Next.js Build",
        cwd=frontend,
        shell=True
    )
    
    # Print Summary
    print_header("TEST SUMMARY")
    for step, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {step.capitalize()}")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed < total:
        print("\n⚠️  Some tests failed. Review errors above.")
        return 1
    
    # Step 5: Start Dev Server
    print_header("STEP 5: Starting Development Server")
    print("\n🚀 Starting Next.js development server...")
    print("   URL: http://localhost:3000")
    print("\n📋 Test Checklist:")
    print("   [ ] Home page loads")
    print("   [ ] Projects page works")
    print("   [ ] Tasks page works")
    print("   [ ] Links are blocked (check console)")
    print("   [ ] Dropdowns toggle")
    print("   [ ] Horizontal scroll works")
    print("   [ ] No garbage text visible")
    print("   [ ] Background color is #F7F7F7")
    
    print("\n⏳ Server will start in 3 seconds...")
    time.sleep(1)
    print("   3...")
    time.sleep(1)
    print("   2...")
    time.sleep(1)
    print("   1...")
    
    # Open browser
    print("\n🌐 Opening browser...")
    webbrowser.open('http://localhost:3000')
    
    print("\n" + "="*70)
    print("  Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    # Start dev server (this blocks)
    try:
        subprocess.run(
            ['npm', 'run', 'dev'],
            cwd=frontend,
            shell=True
        )
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped by user")
        return 0
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
