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

def escape_jsx_text(text):
    """Escape text for JSX"""
    if not text:
        return text
    text = text.replace('{', '&#123;').replace('}', '&#125;')
    return text

def convert_style_to_object(style_str):
    """Convert CSS style string to JSX style object string"""
    if not style_str:
        return '{}'
    
    styles = {}
    for prop in style_str.split(';'):
        prop = prop.strip()
        if ':' in prop:
            key, value = prop.split(':', 1)
            key = key.strip()
            value = value.strip()
            key = re.sub(r'-([a-z])', lambda m: m.group(1).upper(), key)
            value = value.strip('"\'')
            # Escape quotes in value
            value = value.replace('"', '\\"').replace("'", "\\'")
            styles[key] = value
    
    if not styles:
        return '{}'
    
    style_parts = [f'"{k}": "{v}"' for k, v in styles.items()]
    return '{' + ', '.join(style_parts) + '}'

class HTMLToJSXConverter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.jsx_parts = []
        self.tag_stack = []
        
    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        
        if tag_lower in ['script', 'style']:
            return
        
        jsx_attrs = []
        for attr, value in attrs:
            if attr is None:
                continue
            if should_remove_attr(attr):
                continue
            
            jsx_attr = convert_attr_name(attr)
            
            if value is None:
                jsx_attrs.append(jsx_attr)
            else:
                # Escape quotes and special characters
                value_escaped = value.replace('\\', '\\\\').replace('"', '&quot;').replace("'", "&#39;")
                
                if jsx_attr == 'style':
                    style_obj = convert_style_to_object(value)
                    jsx_attrs.append(f'style={{{style_obj}}}')
                else:
                    jsx_attrs.append(f'{jsx_attr}="{value_escaped}"')
        
        attrs_str = ' ' + ' '.join(jsx_attrs) if jsx_attrs else ''
        
        void_tags = ['img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 
                    'col', 'embed', 'source', 'track', 'wbr', 'param', 'iframe']
        if tag_lower in void_tags:
            self.jsx_parts.append(f'<{tag}{attrs_str} />')
        else:
            self.jsx_parts.append(f'<{tag}{attrs_str}>')
            self.tag_stack.append(tag)
    
    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in ['script', 'style']:
            return
        
        if self.tag_stack and self.tag_stack[-1].lower() == tag_lower:
            self.tag_stack.pop()
            self.jsx_parts.append(f'</{tag}>')
    
    def handle_data(self, data):
        data = data.strip()
        if data:
            data = escape_jsx_text(data)
            self.jsx_parts.append(data)
    
    def handle_entityref(self, name):
        self.jsx_parts.append(f'&{name};')
    
    def handle_charref(self, name):
        self.jsx_parts.append(f'&#{name};')

def convert_html_to_jsx(html_content):
    """Convert HTML string to JSX string"""
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<!DOCTYPE[^>]*>', '', html_content, flags=re.IGNORECASE)
    
    parser = HTMLToJSXConverter()
    try:
        parser.feed(html_content)
    except Exception as e:
        print(f"[WARN] Parser error: {e}")
    
    jsx = ''.join(parser.jsx_parts)
    jsx = re.sub(r'>\s+<', '><', jsx)
    jsx = re.sub(r'\s+', ' ', jsx)
    
    return jsx

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

def extract_main_content(jsx_content):
    """Extract main content, excluding already extracted components"""
    main_content = jsx_content
    replacements = []
    
    patterns = [
        (r'<div[^>]*className="[^"]*GlobalTopbar[^"]*"[^>]*>', 'Topbar'),
        (r'<div[^>]*className="[^"]*ModalManager[^"]*"[^>]*>', 'ModalManager'),
        (r'<div[^>]*className="[^"]*ToastStateManager[^"]*"[^>]*>', 'ToastManager'),
        (r'<div[^>]*className="[^"]*LayerDestination[^"]*"[^>]*>', 'LayerDestination'),
    ]
    
    for pattern, name in patterns:
        match = re.search(pattern, main_content, re.IGNORECASE)
        if match:
            start = match.start()
            end = find_matching_closing_tag(main_content, start)
            if end > start:
                replacements.append((start, end))
                print(f"[INFO] Removed {name}: {end - start} chars")
    
    replacements.sort(reverse=True, key=lambda x: x[0])
    for start, end in replacements:
        main_content = main_content[:start] + main_content[end:]
    
    return main_content.strip()

def fix_jsx_syntax(jsx_content):
    """Fix common JSX syntax errors"""
    # Fix style attributes that might have issues
    # Replace style={{...}} with properly escaped versions
    jsx_content = re.sub(r'style=\{\{([^}]+)\}\}', lambda m: f'style={{{m.group(1)}}}', jsx_content)
    
    # Ensure all link tags are self-closing
    jsx_content = re.sub(r'<link([^>]*?)(?<!/)>', r'<link\1 />', jsx_content)
    
    # Ensure all iframe tags are self-closing
    jsx_content = re.sub(r'<iframe([^>]*?)(?<!/)>', r'<iframe\1 />', jsx_content)
    
    # Fix any ><div issues
    jsx_content = re.sub(r'><div', r'<div', jsx_content)
    
    return jsx_content

def regenerate_home_ui():
    """Regenerate Home.jsx with proper JSX syntax"""
    print("[INFO] Loading home.json...")
    with open("agent/extracted/home.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    html = data.get("html", "")
    print(f"[INFO] HTML length: {len(html)} characters")
    
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
    if body_match:
        html = body_match.group(1)
        print("[INFO] Extracted body content")
    
    print("[INFO] Converting HTML to JSX...")
    jsx_content = convert_html_to_jsx(html)
    print(f"[INFO] Generated JSX length: {len(jsx_content)} characters")
    
    print("[INFO] Extracting main content (excluding components)...")
    main_content = extract_main_content(jsx_content)
    print(f"[INFO] Main content length: {len(main_content)} characters")
    
    # Fix JSX syntax
    print("[INFO] Fixing JSX syntax...")
    main_content = fix_jsx_syntax(main_content)
    
    # Wrap in a single div to ensure one parent element
    main_content = f'<div className="asana-content">{main_content}</div>'
    
    # Create the Home.jsx file
    home_jsx = f"""'use client';

import dynamic from 'next/dynamic';
import Topbar from '../components/Topbar';
import ModalManager from '../components/ModalManager';
import ToastManager from '../components/ToastManager';
import LayerDestination from '../components/LayerDestination';

// Large generated content component
function HomeGeneratedContent() {{
  return (
    <div className="w-full h-full overflow-auto">
      {main_content}
    </div>
  );
}}

// Disable SSR for large content to prevent build errors
const SafeLargeUI = dynamic(() => Promise.resolve(HomeGeneratedContent), {{ ssr: false }});

// Main HomeUI component
export default function HomeUI() {{
  return (
    <div className="w-full h-full">
      <ModalManager />
      <ToastManager />
      <LayerDestination />
      <Topbar />
      <SafeLargeUI />
    </div>
  );
}}
"""
    
    output_path = "frontend/generated/Home.jsx"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(home_jsx)
    
    print(f"[SUCCESS] Home.jsx regenerated successfully at {output_path}")
    print(f"[INFO] File size: {len(home_jsx):,} characters")

if __name__ == "__main__":
    regenerate_home_ui()

