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
    # Basic HTML escaping
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
            
            # For dangerouslySetInnerHTML, keep HTML attributes as-is (use 'class' not 'className')
            # Only convert specific attributes that need conversion
            if attr.lower() == 'for':
                html_attr = 'for'  # Keep as 'for' in HTML
            else:
                html_attr = attr  # Keep original attribute name
            
            if value is None:
                html_attrs.append(html_attr)
            else:
                # Escape HTML in attribute values
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
    
    # Fix any malformed tags (like "v class=" should be "<div class=")
    html = re.sub(r'>v class="', r'><div class="', html)
    html = re.sub(r'>([a-z]) class="', r'><\1 class="', html)
    
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

def regenerate_home_ui():
    """Regenerate Home.jsx using dangerouslySetInnerHTML for large content"""
    print("[INFO] Loading home.json...")
    with open("agent/extracted/home.json", "r", encoding="utf-8") as f:
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
    
    # Escape the HTML for use in JSX string
    # Escape backticks and ${} for template literals
    main_content_escaped = main_content.replace('`', '\\`').replace('${', '\\${')
    
    # Create the Home.jsx file using dangerouslySetInnerHTML
    home_jsx = f"""'use client';

import dynamic from 'next/dynamic';
import Topbar from '../components/Topbar';
import ModalManager from '../components/ModalManager';
import ToastManager from '../components/ToastManager';
import LayerDestination from '../components/LayerDestination';

// Large generated content component using dangerouslySetInnerHTML
function HomeGeneratedContent() {{
  const htmlContent = `{main_content_escaped}`;
  
  return (
    <div className="w-full h-full overflow-auto">
      <div dangerouslySetInnerHTML={{{{ __html: htmlContent }}}} />
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

