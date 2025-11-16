import re
import os

def analyze_topbar(file_path):
    """Analyze Topbar.jsx for issues"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Check for dataTestid (should be data-testid)
    if 'dataTestid' in content:
        count = len(re.findall(r'dataTestid=', content))
        issues.append(f'dataTestid used {count} times (should be data-testid)')
    
    # Check if content is all on one line (readability)
    lines = content.split('\n')
    non_empty_lines = [l for l in lines if l.strip()]
    if len(non_empty_lines) <= 5:
        issues.append('File is mostly on one line (readability issue)')
    
    # Check for proper React attributes
    # aria-* should be camelCase (ariaLabel is correct)
    # data-* should be hyphenated (data-testid is correct)
    
    return issues

def analyze_projects(file_path):
    """Analyze Projects.jsx for issues"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Check if component name matches filename
    if 'LoadingScreen' in content and 'Projects' not in content:
        issues.append('Component is named LoadingScreen but file is Projects.jsx (name mismatch)')
    
    # Check if it exports the wrong component
    if 'export default LoadingScreen' in content:
        issues.append('Exports LoadingScreen instead of Projects component')
    
    return issues

def fix_topbar(file_path):
    """Fix Topbar.jsx issues"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix dataTestid to data-testid
    content = re.sub(r'dataTestid=', 'data-testid=', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[SUCCESS] Fixed Topbar.jsx")

def fix_projects(file_path):
    """Fix Projects.jsx - should be a Projects component, not LoadingScreen"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace LoadingScreen with Projects
    content = content.replace('const LoadingScreen = () => {', 'const Projects = () => {')
    content = content.replace('export default LoadingScreen;', 'export default Projects;')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[SUCCESS] Fixed Projects.jsx component name")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    topbar_path = os.path.join(script_dir, "..", "frontend", "components", "Topbar.jsx")
    projects_path = os.path.join(script_dir, "..", "frontend", "generated", "Projects.jsx")
    
    print("=== ANALYZING COMPONENTS ===\n")
    
    if os.path.exists(topbar_path):
        print("Topbar.jsx:")
        issues = analyze_topbar(topbar_path)
        if issues:
            for issue in issues:
                print(f"  ❌ {issue}")
        else:
            print("  ✅ No issues found")
        print()
    
    if os.path.exists(projects_path):
        print("Projects.jsx:")
        issues = analyze_projects(projects_path)
        if issues:
            for issue in issues:
                print(f"  ❌ {issue}")
        else:
            print("  ✅ No issues found")
        print()
    
    print("=== FIXING ISSUES ===\n")
    
    if os.path.exists(topbar_path):
        fix_topbar(topbar_path)
    
    if os.path.exists(projects_path):
        fix_projects(projects_path)
    
    print("\n=== RE-ANALYZING AFTER FIXES ===\n")
    
    if os.path.exists(topbar_path):
        print("Topbar.jsx:")
        issues = analyze_topbar(topbar_path)
        if issues:
            for issue in issues:
                print(f"  ❌ {issue}")
        else:
            print("  ✅ All issues fixed!")
        print()
    
    if os.path.exists(projects_path):
        print("Projects.jsx:")
        issues = analyze_projects(projects_path)
        if issues:
            for issue in issues:
                print(f"  ❌ {issue}")
        else:
            print("  ✅ All issues fixed!")

