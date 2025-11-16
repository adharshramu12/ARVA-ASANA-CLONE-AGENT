import json
import re
import os
from html.parser import HTMLParser

def convert_attr_name(attr):
    """Convert HTML attribute names to JSX"""
    attr_map = {
        'class': 'className',
        'for': 'htmlFor',
        'tabindex': 'tabIndex',
        'readonly': 'readOnly',
        'maxlength': 'maxLength',
        'cellpadding': 'cellPadding',
        'cellspacing': 'cellSpacing',
        'rowspan': 'rowSpan',
        'colspan': 'colSpan',
        'usemap': 'useMap',
        'frameborder': 'frameBorder',
        'contenteditable': 'contentEditable',
    }
    return attr_map.get(attr.lower(), attr)

def should_remove_attr(attr):
    """Check if attribute should be removed"""
    attr_lower = attr.lower()
    if attr_lower.startswith('on'):
        return True
    return False

def escape_html_text(text):
    """Escape text for HTML"""
    if not text:
        return text
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

class HTMLToHTMLConverter(HTMLParser):
    """Convert HTML to clean HTML (for dangerouslySetInnerHTML)"""
    def __init__(self):
        super().__init__()
        self.html_parts = []
        self.tag_stack = []
        
    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        
        if tag_lower in ['script', 'style']:
            return
        
        html_attrs = []
        for attr, value in attrs:
            if attr is None:
                continue
            if should_remove_attr(attr):
                continue
            
            html_attr = attr
            
            if value is None:
                html_attrs.append(html_attr)
            else:
                value_escaped = value.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&#39;')
                html_attrs.append(f'{html_attr}="{value_escaped}"')
        
        attrs_str = ' ' + ' '.join(html_attrs) if html_attrs else ''
        
        void_tags = ['img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 
                    'col', 'embed', 'source', 'track', 'wbr', 'param', 'iframe']
        if tag_lower in void_tags:
            self.html_parts.append(f'<{tag}{attrs_str} />')
        else:
            self.html_parts.append(f'<{tag}{attrs_str}>')
            self.tag_stack.append(tag)
    
    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in ['script', 'style']:
            return
        
        if self.tag_stack and self.tag_stack[-1].lower() == tag_lower:
            self.tag_stack.pop()
            self.html_parts.append(f'</{tag}>')
    
    def handle_data(self, data):
        if data.strip():
            data = escape_html_text(data)
            self.html_parts.append(data)
    
    def handle_entityref(self, name):
        self.html_parts.append(f'&{name};')
    
    def handle_charref(self, name):
        self.html_parts.append(f'&#{name};')

def convert_svg_attr_name(attr_name):
    """Convert SVG attribute names to React JSX camelCase format"""
    attr_lower = attr_name.lower()
    
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
        'xmlns:xlink': 'xmlnsXlink',
    }
    
    if attr_lower in svg_attr_map:
        return svg_attr_map[attr_lower]
    
    # Convert kebab-case to camelCase
    if '-' in attr_name:
        parts = attr_name.split('-')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])
    
    # Convert colon-separated to camelCase
    if ':' in attr_name:
        parts = attr_name.split(':')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])
    
    return attr_name

def fix_svg_attributes_in_html(html_content):
    """Fix all SVG attributes in HTML to React JSX camelCase format"""
    # Fix specific SVG attributes
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
    
    for old_attr, new_attr in svg_attr_replacements.items():
        html_content = re.sub(
            rf'\b{re.escape(old_attr)}\s*=\s*',
            f'{new_attr}=',
            html_content,
            flags=re.IGNORECASE
        )
    
    # Fix any kebab-case SVG attributes
    def fix_kebab_attr(match):
        attr_name = match.group(1)
        fixed = convert_svg_attr_name(attr_name)
        if fixed != attr_name:
            return f'{fixed}='
        return match.group(0)
    
    html_content = re.sub(
        r'\b([a-z]+(?:-[a-z]+)+)\s*=\s*',
        fix_kebab_attr,
        html_content,
        flags=re.IGNORECASE
    )
    
    return html_content

def convert_html_to_clean_html(html_content):
    """Convert HTML to clean HTML for dangerouslySetInnerHTML"""
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<!DOCTYPE[^>]*>', '', html_content, flags=re.IGNORECASE)
    
    parser = HTMLToHTMLConverter()
    try:
        parser.feed(html_content)
    except Exception as e:
        print(f"[WARN] Parser error: {e}")
    
    html = ''.join(parser.html_parts)
    
    # Fix any malformed tags
    html = re.sub(r'>v class="', r'><div class="', html)
    html = re.sub(r'>([a-z]) class="', r'><\1 class="', html)
    
    # Ensure all void tags are self-closing
    html = re.sub(r'<link([^>]*?)(?<!/)>', r'<link\1 />', html)
    html = re.sub(r'<img([^>]*?)(?<!/)>', r'<img\1 />', html)
    html = re.sub(r'<meta([^>]*?)(?<!/)>', r'<meta\1 />', html)
    html = re.sub(r'<input([^>]*?)(?<!/)>', r'<input\1 />', html)
    html = re.sub(r'<br([^>]*?)(?<!/)>', r'<br\1 />', html)
    html = re.sub(r'<iframe([^>]*?)(?<!/)>', r'<iframe\1 />', html)
    
    # Fix SVG attributes to React JSX format
    html = fix_svg_attributes_in_html(html)
    
    return html

def find_matching_closing_tag(content, start_pos, tag_name='div'):
    """Find the matching closing tag for an opening tag"""
    depth = 0
    pos = start_pos
    open_tag_pattern = f'<{tag_name}'
    close_tag = f'</{tag_name}>'
    
    tag_end = content.find('>', start_pos)
    if tag_end == -1:
        return -1
    
    if tag_end > 0 and content[tag_end - 1] == '/':
        return tag_end + 1
    
    pos = tag_end + 1
    depth = 1
    
    while pos < len(content) and depth > 0:
        next_open = content.find(open_tag_pattern, pos)
        next_close = content.find(close_tag, pos)
        
        if next_open == -1 and next_close == -1:
            return -1
        
        if next_open != -1 and (next_close == -1 or next_open < next_close):
            tag_end_pos = content.find('>', next_open, next_open + 200)
            if tag_end_pos != -1 and content[tag_end_pos - 1] == '/':
                pos = tag_end_pos + 1
                continue
            depth += 1
            pos = next_open + len(open_tag_pattern)
        else:
            depth -= 1
            if depth == 0:
                return next_close + len(close_tag)
            pos = next_close + len(close_tag)
    
    return -1

def extract_main_content(html_content):
    """Extract main content, excluding already extracted components"""
    main_content = html_content
    replacements = []
    
    patterns = [
        (r'<div[^>]*(?:class|className)="[^"]*GlobalTopbar[^"]*"[^>]*>', 'Topbar'),
        (r'<div[^>]*(?:class|className)="[^"]*ModalManager[^"]*"[^>]*>', 'ModalManager'),
        (r'<div[^>]*(?:class|className)="[^"]*ToastStateManager[^"]*"[^>]*>', 'ToastManager'),
        (r'<div[^>]*(?:class|className)="[^"]*LayerDestination[^"]*"[^>]*>', 'LayerDestination'),
    ]
    
    for pattern, name in patterns:
        matches = list(re.finditer(pattern, main_content, re.IGNORECASE))
        for match in matches:
            start = match.start()
            end = find_matching_closing_tag(main_content, start)
            if end > start:
                replacements.append((start, end))
                print(f"[INFO] Removed {name}: {end - start} chars")
    
    replacements.sort(reverse=True, key=lambda x: x[0])
    for start, end in replacements:
        main_content = main_content[:start] + main_content[end:]
    
    return main_content.strip()

def generate_ui_component(name):
    """Generate UI component for Projects or Tasks"""
    print(f"[INFO] Generating {name.capitalize()}.jsx...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "extracted", f"{name}.json")
    
    if not os.path.exists(json_path):
        print(f"[ERROR] {json_path} not found")
        return
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    html = data.get("html", "")
    print(f"[INFO] HTML length: {len(html)} characters")
    
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
    if body_match:
        html = body_match.group(1)
        print("[INFO] Extracted body content")
    
    print("[INFO] Converting HTML to clean HTML...")
    clean_html = convert_html_to_clean_html(html)
    print(f"[INFO] Clean HTML length: {len(clean_html)} characters")
    
    print("[INFO] Extracting main content (excluding components)...")
    main_content = extract_main_content(clean_html)
    print(f"[INFO] Main content length: {len(main_content)} characters")
    
    # Escape the HTML for use in JSX template literal
    main_content_escaped = main_content.replace('`', '\\`').replace('${', '\\${').replace('\\', '\\\\')
    
    # Component name
    component_name = name.capitalize()
    
    # Create the component file
    component_jsx = f"""'use client';

import dynamic from "next/dynamic";
import Topbar from "../components/Topbar";
import ModalManager from "../components/ModalManager";
import ToastManager from "../components/ToastManager";
import LayerDestination from "../components/LayerDestination";
import {{ sanitizeHtml }} from "../lib/sanitizeHtml";

// Large generated content component using dangerouslySetInnerHTML
function {component_name}GeneratedContent() {{
  const htmlContent = sanitizeHtml(`{main_content_escaped}`);
  
  return (
    <div className="w-full h-full overflow-auto">
      <div dangerouslySetInnerHTML={{{{ __html: htmlContent }}}} />
    </div>
  );
}}

// Disable SSR for large content to prevent build errors
const SafeLargeUI = dynamic(() => Promise.resolve({component_name}GeneratedContent), {{
  ssr: false,
}});

// Main {component_name}UI component
export default function {component_name}UI() {{
  return (
    <div className="w-full h-full overflow-auto">
      <ModalManager />
      <ToastManager />
      <LayerDestination />
      <Topbar />
      <SafeLargeUI />
    </div>
  );
}}
"""
    
    # Write to file
    output_path = os.path.join(script_dir, "..", "frontend", "generated", f"{component_name}.jsx")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(component_jsx)
    
    print(f"[SUCCESS] {component_name}.jsx generated successfully at {output_path}")
    print(f"[INFO] File size: {len(component_jsx):,} characters")
    print(f"[INFO] Main content size: {len(main_content):,} characters")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        name = sys.argv[1]
        if name in ['projects', 'tasks']:
            generate_ui_component(name)
        else:
            print(f"[ERROR] Invalid name: {name}. Use 'projects' or 'tasks'")
    else:
        # Generate both by default
        generate_ui_component('projects')
        generate_ui_component('tasks')

