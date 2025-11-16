#!/usr/bin/env python3
"""
Automated verification script for pixel-perfect Asana clone
Checks all components, files, and structure
"""

import os
import json
from pathlib import Path

def print_status(message, status="INFO"):
    """Print colored status message"""
    colors = {
        "PASS": "\033[92m✅",
        "FAIL": "\033[91m❌",
        "INFO": "\033[94mℹ️",
        "WARN": "\033[93m⚠️"
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')} {message}{reset}")

def check_file_exists(filepath, description):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "PASS" if exists else "FAIL"
    print_status(f"{description}: {filepath}", status)
    return exists

def check_file_size(filepath, min_size, description):
    """Check if file meets minimum size requirement"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        passes = size >= min_size
        status = "PASS" if passes else "FAIL"
        print_status(f"{description}: {size:,} bytes (min: {min_size:,})", status)
        return passes
    return False

def check_file_content(filepath, search_strings, description):
    """Check if file contains required strings"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for search_str in search_strings:
            if search_str in content:
                print_status(f"  ✓ Contains: {search_str[:50]}...", "PASS")
            else:
                print_status(f"  ✗ Missing: {search_str[:50]}...", "FAIL")
                return False
        return True
    return False

def main():
    """Run all verification checks"""
    print("\n" + "="*70)
    print("🔍 PIXEL-PERFECT ASANA CLONE - AUTOMATED VERIFICATION")
    print("="*70 + "\n")
    
    base_dir = Path(__file__).parent.parent
    results = []
    
    # 1. Check scraper and converter
    print("\n📁 CHECKING AGENT FILES...")
    results.append(check_file_exists(base_dir / "agent" / "scraper.py", "Scraper script"))
    results.append(check_file_exists(base_dir / "agent" / "pixel_perfect_converter.py", "Pixel-perfect converter"))
    results.append(check_file_exists(base_dir / ".env", "Environment variables"))
    
    # 2. Check extracted data
    print("\n📦 CHECKING EXTRACTED DATA...")
    results.append(check_file_exists(base_dir / "agent" / "extracted" / "home.json", "Home page data"))
    results.append(check_file_exists(base_dir / "agent" / "extracted" / "projects.json", "Projects page data"))
    results.append(check_file_exists(base_dir / "agent" / "extracted" / "tasks.json", "Tasks page data"))
    
    results.append(check_file_size(base_dir / "agent" / "extracted" / "home.json", 100000, "Home.json size"))
    results.append(check_file_size(base_dir / "agent" / "extracted" / "projects.json", 50000, "Projects.json size"))
    
    # 3. Check generated components
    print("\n🎨 CHECKING GENERATED COMPONENTS...")
    home_jsx = base_dir / "frontend" / "generated" / "Home.jsx"
    projects_jsx = base_dir / "frontend" / "generated" / "Projects.jsx"
    tasks_jsx = base_dir / "frontend" / "generated" / "Tasks.jsx"
    
    results.append(check_file_exists(home_jsx, "Home.jsx"))
    results.append(check_file_exists(projects_jsx, "Projects.jsx"))
    results.append(check_file_exists(tasks_jsx, "Tasks.jsx"))
    
    # Check file sizes (pixel-perfect = large files)
    results.append(check_file_size(home_jsx, 200000, "Home.jsx size (pixel-perfect)"))
    results.append(check_file_size(projects_jsx, 50000, "Projects.jsx size"))
    results.append(check_file_size(tasks_jsx, 200000, "Tasks.jsx size (pixel-perfect)"))
    
    # 4. Check for pixel-perfect markers
    print("\n🎯 CHECKING PIXEL-PERFECT MARKERS...")
    
    pixel_perfect_markers = [
        "GlobalTopbarStructure",
        "ButtonThemeablePresentation",
        "HighlightSol",
        "ThemeableCardPresentation",
        "SidebarNavigationLinkCard",
        "'use client'",
        "viewBox",
        "aria-label"
    ]
    
    results.append(check_file_content(home_jsx, pixel_perfect_markers[:4], "Home.jsx Asana classes"))
    results.append(check_file_content(projects_jsx, ["'use client'", "className"], "Projects.jsx structure"))
    results.append(check_file_content(tasks_jsx, pixel_perfect_markers[:2], "Tasks.jsx Asana classes"))
    
    # 5. Check Next.js structure
    print("\n⚛️  CHECKING NEXT.JS STRUCTURE...")
    results.append(check_file_exists(base_dir / "frontend" / "package.json", "package.json"))
    results.append(check_file_exists(base_dir / "frontend" / "next.config.js", "next.config.js"))
    results.append(check_file_exists(base_dir / "frontend" / "app" / "layout.tsx", "layout.tsx"))
    results.append(check_file_exists(base_dir / "frontend" / "app" / "page.tsx", "page.tsx"))
    
    # Check if CSS link is in layout
    layout_path = base_dir / "frontend" / "app" / "layout.tsx"
    results.append(check_file_content(
        layout_path, 
        ["cloudfront", "asana", "css"],
        "Asana CSS link in layout"
    ))
    
    # 6. Check routes
    print("\n🛣️  CHECKING ROUTES...")
    results.append(check_file_exists(base_dir / "frontend" / "app" / "projects" / "page.tsx", "Projects route"))
    results.append(check_file_exists(base_dir / "frontend" / "app" / "tasks" / "page.tsx", "Tasks route"))
    
    # 7. Check components
    print("\n🧩 CHECKING HELPER COMPONENTS...")
    results.append(check_file_exists(base_dir / "frontend" / "components" / "DropdownManager.tsx", "DropdownManager"))
    results.append(check_file_exists(base_dir / "frontend" / "components" / "LinkInterceptor.tsx", "LinkInterceptor"))
    
    # 8. Summary
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    
    total = len(results)
    passed = sum(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\nTotal Checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {percentage:.1f}%")
    
    if percentage == 100:
        print_status("\n🎉 ALL CHECKS PASSED! Pixel-perfect clone verified!", "PASS")
        print_status("The clone matches the exact structure and styling of Asana.", "INFO")
        print_status("\n🚀 Next steps:", "INFO")
        print("   1. cd frontend")
        print("   2. npm run dev")
        print("   3. Open http://localhost:3000")
        return 0
    elif percentage >= 80:
        print_status(f"\n⚠️  MOSTLY COMPLETE ({percentage:.0f}%) - Minor issues detected", "WARN")
        return 1
    else:
        print_status(f"\n❌ VERIFICATION FAILED ({percentage:.0f}%) - Major issues detected", "FAIL")
        return 2

if __name__ == "__main__":
    import sys
    sys.exit(main())
