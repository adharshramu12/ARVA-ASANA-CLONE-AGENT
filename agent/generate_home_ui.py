import json
import re
import os
from html.parser import HTMLParser

# Reuse the conversion functions from html_to_jsx.py
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
    # Remove event handlers
    if attr_lower.startswith('on'):
        return True
    return False

def escape_jsx_text(text):
    """Escape text for JSX"""
    if not text:
        return text
    # Escape curly braces
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
        
        # Skip script and style tags completely
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
                value_escaped = value.replace('"', '&quot;').replace("'", "&#39;")
                if jsx_attr == 'style':
                    style_obj = convert_style_to_object(value)
                    jsx_attrs.append(f'style={{{style_obj}}}')
                else:
                    jsx_attrs.append(f'{jsx_attr}="{value_escaped}"')
        
        attrs_str = ' ' + ' '.join(jsx_attrs) if jsx_attrs else ''
        
        void_tags = ['img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 
                    'col', 'embed', 'source', 'track', 'wbr', 'param']
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
    
    # Remove Topbar
    topbar_pattern = r'<div[^>]*className="[^"]*GlobalTopbar[^"]*"[^>]*>'
    topbar_match = re.search(topbar_pattern, main_content, re.IGNORECASE)
    if topbar_match:
        start = topbar_match.start()
        end = find_matching_closing_tag(main_content, start)
        if end > start:
            replacements.append((start, end))
            print(f"[INFO] Removed Topbar: {end - start} chars")
    
    # Remove ModalManager
    modal_pattern = r'<div[^>]*className="[^"]*ModalManager[^"]*"[^>]*>'
    modal_match = re.search(modal_pattern, main_content, re.IGNORECASE)
    if modal_match:
        start = modal_match.start()
        end = find_matching_closing_tag(main_content, start)
        if end > start:
            replacements.append((start, end))
            print(f"[INFO] Removed ModalManager: {end - start} chars")
    
    # Remove ToastManager
    toast_pattern = r'<div[^>]*className="[^"]*ToastStateManager[^"]*"[^>]*>'
    toast_match = re.search(toast_pattern, main_content, re.IGNORECASE)
    if toast_match:
        start = toast_match.start()
        end = find_matching_closing_tag(main_content, start)
        if end > start:
            replacements.append((start, end))
            print(f"[INFO] Removed ToastManager: {end - start} chars")
    
    # Remove LayerDestination
    layer_pattern = r'<div[^>]*className="[^"]*LayerDestination[^"]*"[^>]*>'
    layer_match = re.search(layer_pattern, main_content, re.IGNORECASE)
    if layer_match:
        start = layer_match.start()
        end = find_matching_closing_tag(main_content, start)
        if end > start:
            replacements.append((start, end))
            print(f"[INFO] Removed LayerDestination: {end - start} chars")
    
    # Apply replacements in reverse order
    replacements.sort(reverse=True, key=lambda x: x[0])
    for start, end in replacements:
        main_content = main_content[:start] + main_content[end:]
    
    return main_content.strip()

def generate_home_ui():
    """Generate the complete Home.jsx file"""
    print("[INFO] Loading home.json...")
    with open("agent/extracted/home.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    html = data.get("html", "")
    print(f"[INFO] HTML length: {len(html)} characters")
    
    # Extract body content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
    if body_match:
        html = body_match.group(1)
        print("[INFO] Extracted body content")
    
    # Convert to JSX
    print("[INFO] Converting HTML to JSX...")
    jsx_content = convert_html_to_jsx(html)
    print(f"[INFO] Generated JSX length: {len(jsx_content)} characters")
    
    # Extract main content (excluding components)
    print("[INFO] Extracting main content (excluding components)...")
    main_content = extract_main_content(jsx_content)
    print(f"[INFO] Main content length: {len(main_content)} characters")
    
    # Indent main content for proper JSX formatting
    main_content_lines = main_content.split('\n')
    if len(main_content_lines) == 1:
        # All on one line, just add indentation
        indented_content = '      ' + main_content
    else:
        # Multiple lines, indent each
        indented_content = '\n'.join(['      ' + line if line.strip() else line for line in main_content_lines])
    
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
{indented_content}
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
    
    # Write to file
    output_path = "frontend/generated/Home.jsx"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(home_jsx)
    
    print(f"[SUCCESS] Home.jsx generated successfully at {output_path}")
    print(f"[INFO] File size: {len(home_jsx):,} characters")
    print(f"[INFO] Main content size: {len(main_content):,} characters")

if __name__ == "__main__":
    generate_home_ui()

