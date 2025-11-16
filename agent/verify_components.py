import re
import os

def verify_file(file_path):
    """Verify SVG attributes in a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Check for lowercase SVG attributes that should be camelCase
    checks = [
        ('viewbox', 'viewBox'),
        ('lineargradient', 'linearGradient'),
        ('gradientunits', 'gradientUnits'),
        ('gradienttransform', 'gradientTransform'),
        ('stopcolor', 'stopColor'),
        ('stopopacity', 'stopOpacity'),
    ]
    
    for wrong, correct in checks:
        # Check for wrong case (but not if correct case exists)
        wrong_matches = list(re.finditer(rf'\b{re.escape(wrong)}\s*=', content, re.IGNORECASE))
        correct_matches = list(re.finditer(rf'\b{re.escape(correct)}\s*=', content))
        
        # Filter wrong matches to exclude those that are actually correct
        actual_wrong = [m for m in wrong_matches if not content[m.start():m.start()+len(correct)].startswith(correct)]
        
        if actual_wrong and not correct_matches:
            issues.append(f'{wrong} (should be {correct})')
        elif actual_wrong:
            # Some wrong, some correct - partial fix needed
            issues.append(f'{wrong} ({len(actual_wrong)} still wrong, {len(correct_matches)} correct)')
    
    # Check for tag names
    if re.search(r'<lineargradient', content, re.IGNORECASE) and not re.search(r'<linearGradient', content):
        issues.append('<lineargradient> tag (should be <linearGradient>)')
    
    return issues

script_dir = os.path.dirname(os.path.abspath(__file__))

files_to_check = [
    os.path.join(script_dir, "..", "frontend", "components", "Topbar.jsx"),
    os.path.join(script_dir, "..", "frontend", "generated", "Projects.jsx"),
]

print("Verifying SVG attributes in component files:\n")
all_good = True

for file_path in files_to_check:
    if os.path.exists(file_path):
        filename = os.path.basename(file_path)
        issues = verify_file(file_path)
        if issues:
            print(f"❌ {filename}:")
            for issue in issues:
                print(f"   - {issue}")
            all_good = False
        else:
            print(f"✅ {filename}: All SVG attributes correct")

if all_good:
    print("\n✅ All component files have correct SVG attributes!")
else:
    print("\n❌ Some files need fixing")

