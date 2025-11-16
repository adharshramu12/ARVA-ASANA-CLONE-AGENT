import json
import re
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
    # Parse style string (e.g., "color: red; background: blue")
    for prop in style_str.split(';'):
        prop = prop.strip()
        if ':' in prop:
            key, value = prop.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Convert kebab-case to camelCase
            key = re.sub(r'-([a-z])', lambda m: m.group(1).upper(), key)
            # Remove quotes from value
            value = value.strip('"\'')
            styles[key] = value
    
    # Convert to JSX object string
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
        
        # Build JSX attributes
        jsx_attrs = []
        for attr, value in attrs:
            if attr is None:
                continue
                
            # Skip unwanted attributes
            if should_remove_attr(attr):
                continue
            
            # Convert attribute name
            jsx_attr = convert_attr_name(attr)
            
            # Handle attribute value
            if value is None:
                jsx_attrs.append(jsx_attr)
            else:
                # Escape quotes
                value_escaped = value.replace('"', '&quot;').replace("'", "&#39;")
                # Handle style attribute - convert to JSX style object
                if jsx_attr == 'style':
                    # Convert CSS string to JSX style object
                    style_obj = convert_style_to_object(value)
                    jsx_attrs.append(f'style={{{style_obj}}}')
                else:
                    jsx_attrs.append(f'{jsx_attr}="{value_escaped}"')
        
        attrs_str = ' ' + ' '.join(jsx_attrs) if jsx_attrs else ''
        
        # Self-closing tags
        void_tags = ['img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 
                    'col', 'embed', 'source', 'track', 'wbr', 'param']
        if tag_lower in void_tags:
            self.jsx_parts.append(f'<{tag}{attrs_str} />')
        else:
            self.jsx_parts.append(f'<{tag}{attrs_str}>')
            self.tag_stack.append(tag)
    
    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        
        # Skip script and style tags
        if tag_lower in ['script', 'style']:
            return
        
        # Close matching tag
        if self.tag_stack and self.tag_stack[-1].lower() == tag_lower:
            self.tag_stack.pop()
            self.jsx_parts.append(f'</{tag}>')
    
    def handle_data(self, data):
        # Clean and escape text
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
    # Remove script and style tags completely
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML comments
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # Remove DOCTYPE and other declarations
    html_content = re.sub(r'<!DOCTYPE[^>]*>', '', html_content, flags=re.IGNORECASE)
    
    # Parse and convert
    parser = HTMLToJSXConverter()
    try:
        parser.feed(html_content)
    except Exception as e:
        print(f"[WARN] Parser error: {e}")
    
    jsx = ''.join(parser.jsx_parts)
    
    # Clean up excessive whitespace between tags
    jsx = re.sub(r'>\s+<', '><', jsx)
    jsx = re.sub(r'\s+', ' ', jsx)
    
    return jsx

def process_home_json():
    """Read home.json and convert to Home.jsx"""
    print("[INFO] Loading home.json...")
    with open("agent/extracted/home.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    html = data.get("html", "")
    print(f"[INFO] HTML length: {len(html)} characters")
    
    # Extract body content if it's a full HTML document
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
    if body_match:
        html = body_match.group(1)
        print("[INFO] Extracted body content")
    
    # Limit size for processing (take first 200000 chars to avoid memory issues)
    # This should be enough for most pages
    original_length = len(html)
    if len(html) > 200000:
        print(f"[WARN] HTML is very large ({len(html)} chars). Processing first 200000 characters...")
        html = html[:200000]
    
    print("[INFO] Converting HTML to JSX...")
    jsx_content = convert_html_to_jsx(html)
    
    print(f"[INFO] Generated JSX length: {len(jsx_content)} characters")
    
    # Create React component
    component = f"""export default function Home() {{
  return (
    <>
{jsx_content}
    </>
  );
}}
"""
    
    # Write to file
    output_path = "frontend/generated/Home.jsx"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(component)
    
    print(f"[SUCCESS] Home.jsx generated successfully at {output_path}")

if __name__ == "__main__":
    process_home_json()

