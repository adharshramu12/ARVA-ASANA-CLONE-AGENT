import re

with open('frontend/generated/Home.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Find HTML content
match = re.search(r'const htmlContent = `(.*?)`;', content, re.DOTALL)
if not match:
    print("Could not find HTML content")
    exit(1)

html_content = match.group(1)

# Check for lowercase SVG attributes (should be 0)
lowercase_attrs = {
    'gradientunits': 'gradientUnits',
    'gradienttransform': 'gradientTransform',
    'lineargradient': 'linearGradient',
    'stopcolor': 'stopColor',
    'stopopacity': 'stopOpacity',
    'viewbox': 'viewBox',
    'preserveaspectratio': 'preserveAspectRatio',
}

print("Checking for SVG attributes in generated file:")
issues_found = False
for old_attr, new_attr in lowercase_attrs.items():
    # Check for lowercase/wrong case versions (case-sensitive for old_attr to avoid false positives)
    # But we need to be careful - check if it's actually the wrong case
    wrong_case_pattern = rf'\b{old_attr}\s*='
    wrong_case_matches = re.findall(wrong_case_pattern, html_content, re.IGNORECASE)
    # Filter to only actual wrong case (not viewBox matching viewbox)
    actual_wrong = [m for m in wrong_case_matches if not m.startswith(new_attr)]
    
    # Check for correct camelCase version
    correct_count = len(re.findall(rf'\b{re.escape(new_attr)}\s*=', html_content))
    
    if actual_wrong:
        print(f"  ❌ {old_attr}: {len(actual_wrong)} occurrences with wrong case (should be {new_attr})")
        issues_found = True
    elif correct_count > 0:
        print(f"  ✅ {new_attr}: {correct_count} occurrences (correct)")
    else:
        print(f"  ⚪ {old_attr}/{new_attr}: not found")

if not issues_found:
    print("\n✅ All SVG attributes are properly formatted!")
else:
    print("\n❌ Some SVG attributes still need fixing")

