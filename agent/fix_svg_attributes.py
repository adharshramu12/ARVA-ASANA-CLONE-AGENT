import re
import os

def convert_svg_attr_name(attr_name):
    """Convert SVG attribute names to React JSX camelCase format"""
    attr_lower = attr_name.lower()
    
    # Direct mappings
    svg_attr_map = {
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
        'text-anchor': 'textAnchor',
        'font-family': 'fontFamily',
        'font-size': 'fontSize',
        'font-weight': 'fontWeight',
        'font-style': 'fontStyle',
        'letter-spacing': 'letterSpacing',
        'word-spacing': 'wordSpacing',
        'text-decoration': 'textDecoration',
        'baseline-shift': 'baselineShift',
        'dominant-baseline': 'dominantBaseline',
        'alignment-baseline': 'alignmentBaseline',
        'xlink:href': 'xlinkHref',
        'xlink:title': 'xlinkTitle',
        'xml:space': 'xmlSpace',
        'xml:lang': 'xmlLang',
        'preserveaspectratio': 'preserveAspectRatio',
        'viewbox': 'viewBox',
        'xmlns': 'xmlns',  # Keep as-is
        'xmlns:xlink': 'xmlnsXlink',
    }
    
    if attr_lower in svg_attr_map:
        return svg_attr_map[attr_lower]
    
    # Convert kebab-case to camelCase (e.g., "fill-opacity" -> "fillOpacity")
    if '-' in attr_name:
        parts = attr_name.split('-')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])
    
    # Convert colon-separated to camelCase (e.g., "xlink:href" -> "xlinkHref")
    if ':' in attr_name:
        parts = attr_name.split(':')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])
    
    return attr_name

def fix_svg_attributes_in_html(html_content):
    """Fix all SVG attributes in HTML content to React JSX camelCase format"""
    
    # Pattern to match attribute="value" or attribute='value' or attribute=value
    # This will match attributes in any tag
    def replace_attr_in_string(match):
        full_match = match.group(0)
        attr_name = match.group(1)
        quote = match.group(2) or ''
        value = match.group(3) or ''
        
        # Convert attribute name
        fixed_attr = convert_svg_attr_name(attr_name)
        
        # Only replace if the name changed
        if fixed_attr != attr_name:
            if value:
                return f'{fixed_attr}={quote}{value}{quote}'
            else:
                return fixed_attr
        
        return full_match
    
    # Fix attributes with values: attr="value" or attr='value' or attr=value
    # Match common SVG attributes (case-insensitive)
    svg_attr_pattern = r'\b(gradientunits|gradienttransform|lineargradient|radialgradient|stopcolor|stopopacity|clip-path|fill-rule|fill-opacity|stroke-width|stroke-linecap|stroke-linejoin|stroke-dasharray|stroke-dashoffset|stroke-miterlimit|stroke-opacity|text-anchor|font-family|font-size|font-weight|font-style|letter-spacing|word-spacing|text-decoration|baseline-shift|dominant-baseline|alignment-baseline|xlink:href|xlink:title|xml:space|xml:lang|preserveaspectratio|viewbox|xmlns:xlink)\s*=\s*(["\']?)([^"\'>\s]*)\2'
    
    html_content = re.sub(svg_attr_pattern, replace_attr_in_string, html_content, flags=re.IGNORECASE)
    
    # Also handle any kebab-case or lowercase SVG attributes we might have missed
    # This is a more general pattern for any attribute that looks like it should be camelCase
    def fix_generic_attr(match):
        attr_name = match.group(1)
        quote = match.group(2) or ''
        value = match.group(3) or ''
        
        # Check if this looks like an SVG attribute that needs fixing
        attr_lower = attr_name.lower()
        if ('-' in attr_name or 
            attr_lower in ['gradientunits', 'gradienttransform', 'lineargradient', 
                          'stopcolor', 'stopopacity', 'preserveaspectratio', 'viewbox'] or
            ':' in attr_name):
            fixed_attr = convert_svg_attr_name(attr_name)
            if value:
                return f'{fixed_attr}={quote}{value}{quote}'
            else:
                return fixed_attr
        
        return match.group(0)
    
    # More general pattern for any attribute
    html_content = re.sub(
        r'\b([a-z]+(?:-[a-z]+)+|[a-z]+:[a-z]+|[a-z]+)\s*=\s*(["\']?)([^"\'>\s]*)\2',
        fix_generic_attr,
        html_content,
        flags=re.IGNORECASE
    )
    
    return html_content

def fix_svg_attributes(file_path):
    """Fix SVG attributes in a JSX file - standalone function for pipeline use"""
    import os
    import re
    
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return False
    
    print(f"[INFO] Reading {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the HTML content in the template literal (may be wrapped in sanitizeHtml())
    # Pattern: const htmlContent = sanitizeHtml(`...`);
    # First find the start and end positions
    start_match = re.search(r'const htmlContent = sanitizeHtml\(`', content)
    if start_match:
        start_pos = start_match.end()
        # Find the closing backtick - it might be followed by `);` on same line or `;\n` (semicolon then newline)
        # First try to find `);` pattern (backtick + closing paren + semicolon on same line)
        end_idx = content.find(chr(96) + ');', start_pos)
        if end_idx < 0:
            # Try finding backtick followed by semicolon and newline (template literal ends with `;)
            # Pattern: `;\n
            pattern = chr(96) + ';\n'
            end_idx = content.find(pattern, start_pos)
            if end_idx < 0:
                # Last resort: find backtick followed by semicolon (might be end of template)
                # Look for `; that's not part of the HTML content
                backtick_semi = content.find(chr(96) + ';', start_pos)
                if backtick_semi > 0:
                    # Verify it's followed by newline or whitespace (not part of HTML)
                    after = content[backtick_semi+2:backtick_semi+10]
                    if '\n' in after or after.strip() == '':
                        end_idx = backtick_semi
        
        if end_idx >= 0:
            end_pos = end_idx
            html_content = content[start_pos:end_pos]
        else:
            print(f"[ERROR] Could not find end of template literal")
            print(f"[DEBUG] Start pos: {start_pos}, Content length: {len(content)}")
            print(f"[DEBUG] Looking for '`);' in content from position {start_pos}")
            # Try to find it manually
            test_idx = content.find('`);', start_pos)
            print(f"[DEBUG] Manual find result: {test_idx}")
            if test_idx < 0:
                # Check if backtick exists at all
                backtick_idx = content.find('`', start_pos)
                print(f"[DEBUG] First backtick after start: {backtick_idx}")
                if backtick_idx > 0:
                    print(f"[DEBUG] Context around backtick: {repr(content[backtick_idx-5:backtick_idx+10])}")
            print(f"[DEBUG] First 200 chars from start: {content[start_pos:start_pos+200]}")
            print(f"[DEBUG] Last 200 chars before end: {content[max(0, len(content)-200):]}")
            return
    else:
        # Try without sanitizeHtml wrapper
        start_match = re.search(r'const htmlContent = `', content)
        if start_match:
            start_pos = start_match.end()
            end_idx = content.find('`;', start_pos)
            if end_idx >= 0:
                end_pos = end_idx
                html_content = content[start_pos:end_pos]
            else:
                print("[ERROR] Could not find end of template literal")
                return
        else:
            print("[ERROR] Could not find htmlContent template literal")
            print(f"[DEBUG] File length: {len(content)} characters")
            return
    
    original_html = html_content
    print(f"[INFO] Found HTML content: {len(html_content)} characters")
    
    # Fix SVG attributes
    print("[INFO] Fixing SVG attributes...")
    
    # Count occurrences before fixing
    patterns_to_fix = {
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
    for old_attr, new_attr in patterns_to_fix.items():
        # Count occurrences (case-insensitive) - but only if they're actually lowercase/mixed
        # We want to find viewbox, ViewBox, VIEWBOX, etc. and convert to viewBox
        pattern = rf'\b{re.escape(old_attr)}\s*=\s*'
        matches = list(re.finditer(pattern, html_content, re.IGNORECASE))
        
        # Filter to only those that aren't already in the correct case
        actual_fixes = []
        for match in matches:
            matched_text = match.group(0)
            # Check if it's already in the correct format
            if not matched_text.startswith(new_attr):
                actual_fixes.append(match)
        
        if actual_fixes:
            # Replace all occurrences (case-insensitive) with the correct camelCase version
            html_content = re.sub(
                pattern,
                f'{new_attr}=',
                html_content,
                flags=re.IGNORECASE
            )
            total_fixes += len(actual_fixes)
            print(f"[INFO] Fixed {len(actual_fixes)} occurrences of {old_attr} -> {new_attr}")
    
    # Also fix any kebab-case attributes that might be SVG-related
    # This catches any attribute with a hyphen that should be camelCase
    def fix_kebab_attr(match):
        full_attr = match.group(1)
        # Check if it's likely an SVG attribute (common patterns)
        if any(pattern in full_attr.lower() for pattern in ['gradient', 'stop', 'clip', 'fill', 'stroke', 'text', 'font', 'baseline', 'xlink', 'xml']):
            fixed = convert_svg_attr_name(full_attr)
            if fixed != full_attr:
                return f'{fixed}='
        return match.group(0)
    
    # Fix kebab-case attributes in SVG context
    html_content = re.sub(
        r'\b([a-z]+(?:-[a-z]+)+)\s*=\s*',
        fix_kebab_attr,
        html_content,
        flags=re.IGNORECASE
    )
    
    # Also fix any other kebab-case SVG attributes
    def fix_kebab_case_attr(match):
        attr_name = match.group(1)
        fixed_attr = convert_svg_attr_name(attr_name)
        if fixed_attr != attr_name:
            return f'{fixed_attr}='
        return match.group(0)
    
    # Fix remaining kebab-case attributes in SVG context
    html_content = re.sub(
        r'\b([a-z]+(?:-[a-z]+)+)\s*=\s*',
        fix_kebab_case_attr,
        html_content,
        flags=re.IGNORECASE
    )
    
    # Ensure all <svg> tags have xmlns attribute
    def add_xmlns_to_svg(match):
        svg_tag = match.group(0)
        if 'xmlns=' not in svg_tag.lower():
            # Insert xmlns after <svg or <svg with attributes
            if '>' in svg_tag:
                svg_tag = svg_tag.replace('>', ' xmlns="http://www.w3.org/2000/svg">', 1)
            else:
                svg_tag = svg_tag + ' xmlns="http://www.w3.org/2000/svg"'
        return svg_tag
    
    html_content = re.sub(
        r'<svg[^>]*>',
        add_xmlns_to_svg,
        html_content,
        flags=re.IGNORECASE
    )
    
    if html_content != original_html:
        print(f"[INFO] Total SVG attribute fixes: {total_fixes}")
        
        # Replace the HTML content in the file
        new_content = content[:start_pos] + html_content + content[end_pos:]
        
        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"[SUCCESS] Fixed SVG attributes in {file_path}")
    else:
        print("[INFO] No SVG attributes needed fixing")

def fix_jsx_svg_attributes(file_name):
    """Fix SVG attributes in a JSX file (wrapper for backward compatibility)"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "..", "frontend", "generated", file_name)
    return fix_svg_attributes(file_path)

def fix_all_svg_attributes():
    """Fix SVG attributes in all generated JSX files"""
    files = ["Home.jsx", "Projects.jsx", "Tasks.jsx"]
    for file_name in files:
        print(f"\n[INFO] Processing {file_name}...")
        fix_jsx_svg_attributes(file_name)

if __name__ == "__main__":
    fix_all_svg_attributes()
