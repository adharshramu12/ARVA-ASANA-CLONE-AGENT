import re
import os

def fix_svg_attributes_in_file(file_path):
    """Fix SVG attributes in a JSX file"""
    print(f"[INFO] Reading {file_path}...")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    original_content = content
    
    # SVG attribute mappings
    svg_attr_replacements = {
        'gradientunits': 'gradientUnits',
        'gradienttransform': 'gradientTransform',
        'lineargradient': 'linearGradient',
        'radialgradient': 'radialGradient',
        'stopcolor': 'stopColor',
        'stopopacity': 'stopOpacity',
        'clip-path': 'clipPath',
        'fill-rule': 'fillRule',
        'fill-opacity': 'fillOpacity',
        'stroke-width': 'strokeWidth',
        'stroke-linecap': 'strokeLinecap',
        'stroke-linejoin': 'strokeLinejoin',
        'stroke-dasharray': 'strokeDasharray',
        'stroke-dashoffset': 'strokeDashoffset',
        'stroke-miterlimit': 'strokeMiterlimit',
        'stroke-opacity': 'strokeOpacity',
        'preserveaspectratio': 'preserveAspectRatio',
        'viewbox': 'viewBox',
    }
    
    total_fixes = 0
    
    for old_attr, new_attr in svg_attr_replacements.items():
        # Find all occurrences (case-insensitive)
        pattern = rf'\b{re.escape(old_attr)}\s*='
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        
        # Filter to only those that aren't already in correct case
        actual_fixes = []
        for match in matches:
            matched_text = match.group(0)
            if not matched_text.startswith(new_attr):
                actual_fixes.append(match)
        
        if actual_fixes:
            # Replace all occurrences
            content = re.sub(
                pattern,
                f'{new_attr}=',
                content,
                flags=re.IGNORECASE
            )
            total_fixes += len(actual_fixes)
            print(f"[INFO] Fixed {len(actual_fixes)} occurrences of {old_attr} -> {new_attr}")
    
    # Also fix kebab-case attributes
    def fix_kebab_attr(match):
        attr_name = match.group(1)
        # Convert kebab-case to camelCase
        if '-' in attr_name:
            parts = attr_name.split('-')
            fixed = parts[0] + ''.join(word.capitalize() for word in parts[1:])
            return f'{fixed}='
        return match.group(0)
    
    # Fix any remaining kebab-case SVG attributes
    content = re.sub(
        r'\b([a-z]+(?:-[a-z]+)+)\s*=\s*',
        fix_kebab_attr,
        content,
        flags=re.IGNORECASE
    )
    
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[SUCCESS] Fixed SVG attributes in {file_path}")
        print(f"[INFO] Total fixes: {total_fixes}")
    else:
        print("[INFO] No SVG attributes needed fixing")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Fix Topbar.jsx
    topbar_path = os.path.join(script_dir, "..", "frontend", "components", "Topbar.jsx")
    if os.path.exists(topbar_path):
        fix_svg_attributes_in_file(topbar_path)
    
    # Fix Projects.jsx
    projects_path = os.path.join(script_dir, "..", "frontend", "generated", "Projects.jsx")
    if os.path.exists(projects_path):
        fix_svg_attributes_in_file(projects_path)
    
    # Also check other component files
    components_dir = os.path.join(script_dir, "..", "frontend", "components")
    if os.path.exists(components_dir):
        for filename in os.listdir(components_dir):
            if filename.endswith('.jsx'):
                file_path = os.path.join(components_dir, filename)
                fix_svg_attributes_in_file(file_path)

