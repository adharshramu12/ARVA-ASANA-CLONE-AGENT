import re
import os
from html.parser import HTMLParser

class ComponentExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.components = {}
        self.current_component = None
        self.component_stack = []
        self.depth = 0
        self.in_target = False
        
    def should_extract(self, tag, attrs):
        """Determine if this element should be extracted as a component"""
        attrs_dict = dict(attrs) if attrs else {}
        className = attrs_dict.get('className', '') or attrs_dict.get('class', '')
        element_id = attrs_dict.get('id', '')
        
        # Check for major component patterns
        patterns = {
            'Topbar': ['GlobalTopbar', 'Topbar', 'topbar', 'header'],
            'Sidebar': ['Sidebar', 'sidebar', 'nav', 'Navigation'],
            'ModalManager': ['ModalManager', 'modal-manager'],
            'ToastManager': ['ToastStateManager', 'Toast', 'toast'],
            'LayerDestination': ['LayerDestination', 'layer'],
        }
        
        for comp_name, keywords in patterns.items():
            if any(kw.lower() in className.lower() or kw.lower() in element_id.lower() for kw in keywords):
                return comp_name
        
        return None
    
    def handle_starttag(self, tag, attrs):
        if not self.in_target:
            component_name = self.should_extract(tag, attrs)
            if component_name:
                self.current_component = component_name
                self.in_target = True
                self.component_stack = []
                self.components[component_name] = {'start': self.getpos(), 'content': []}
        
        if self.in_target:
            self.component_stack.append((tag, attrs))
            # Reconstruct the tag
            attrs_str = ' '.join([f'{k}="{v}"' if v else k for k, v in attrs])
            self.components[self.current_component]['content'].append(f'<{tag} {attrs_str}>' if attrs_str else f'<{tag}>')
            self.depth += 1
    
    def handle_endtag(self, tag):
        if self.in_target:
            self.components[self.current_component]['content'].append(f'</{tag}>')
            self.depth -= 1
            if self.depth == 0:
                self.in_target = False
                self.current_component = None
    
    def handle_data(self, data):
        if self.in_target and data.strip():
            self.components[self.current_component]['content'].append(data.strip())

def find_matching_closing_tag(content, start_pos, tag_name='div'):
    """Find the matching closing tag for an opening tag"""
    depth = 0
    pos = start_pos
    open_tag_pattern = f'<{tag_name}'
    close_tag = f'</{tag_name}>'
    
    # Skip the opening tag we're matching
    # Find where the opening tag ends (either > or />)
    tag_end = content.find('>', start_pos)
    if tag_end == -1:
        return -1
    
    # Check if it's self-closing
    if content[tag_end - 1] == '/':
        return tag_end + 1
    
    pos = tag_end + 1
    depth = 1
    
    while pos < len(content) and depth > 0:
        # Find next opening or closing tag
        next_open = content.find(open_tag_pattern, pos)
        next_close = content.find(close_tag, pos)
        
        if next_open == -1 and next_close == -1:
            return -1
        
        # Determine which comes first
        if next_open != -1 and (next_close == -1 or next_open < next_close):
            # Check if it's a self-closing tag
            tag_end_pos = content.find('>', next_open, next_open + 200)
            if tag_end_pos != -1 and content[tag_end_pos - 1] == '/':
                # Self-closing tag, skip it
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

def extract_major_sections(jsx_content):
    """Extract major sections from JSX using proper tag matching"""
    sections = {}
    replacements = []
    
    # Pattern 1: GlobalTopbarStructure
    topbar_pattern = r'<div[^>]*className="[^"]*GlobalTopbar[^"]*"[^>]*>'
    topbar_match = re.search(topbar_pattern, jsx_content, re.IGNORECASE)
    if topbar_match:
        start = topbar_match.start()
        end = find_matching_closing_tag(jsx_content, start)
        if end > start:
            sections['Topbar'] = jsx_content[start:end]
            replacements.append((start, end, '<Topbar />'))
            print(f"[INFO] Extracted Topbar: {end - start} chars")
    
    # Pattern 2: ModalManager
    modal_pattern = r'<div[^>]*className="[^"]*ModalManager[^"]*"[^>]*>'
    modal_match = re.search(modal_pattern, jsx_content, re.IGNORECASE)
    if modal_match:
        start = modal_match.start()
        end = find_matching_closing_tag(jsx_content, start)
        if end > start:
            sections['ModalManager'] = jsx_content[start:end]
            replacements.append((start, end, '<ModalManager />'))
            print(f"[INFO] Extracted ModalManager: {end - start} chars")
    
    # Pattern 3: ToastStateManager
    toast_pattern = r'<div[^>]*className="[^"]*ToastStateManager[^"]*"[^>]*>'
    toast_match = re.search(toast_pattern, jsx_content, re.IGNORECASE)
    if toast_match:
        start = toast_match.start()
        end = find_matching_closing_tag(jsx_content, start)
        if end > start:
            sections['ToastManager'] = jsx_content[start:end]
            replacements.append((start, end, '<ToastManager />'))
            print(f"[INFO] Extracted ToastManager: {end - start} chars")
    
    # Pattern 4: LayerDestination
    layer_pattern = r'<div[^>]*className="[^"]*LayerDestination[^"]*"[^>]*>'
    layer_match = re.search(layer_pattern, jsx_content, re.IGNORECASE)
    if layer_match:
        start = layer_match.start()
        end = find_matching_closing_tag(jsx_content, start)
        if end > start:
            sections['LayerDestination'] = jsx_content[start:end]
            replacements.append((start, end, '<LayerDestination />'))
            print(f"[INFO] Extracted LayerDestination: {end - start} chars")
    
    # Apply replacements in reverse order to maintain positions
    replacements.sort(reverse=True, key=lambda x: x[0])
    main_content = jsx_content
    for start, end, replacement in replacements:
        main_content = main_content[:start] + replacement + main_content[end:]
    
    sections['MainContent'] = main_content.strip()
    
    return sections

def create_component_file(component_name, jsx_content):
    """Create a component file"""
    # Clean up the JSX content
    jsx_content = jsx_content.strip()
    
    component_code = f"""export default function {component_name}() {{
  return (
    <>
{jsx_content}
    </>
  );
}}
"""
    return component_code

def optimize_home():
    """Main optimization function"""
    print("[INFO] Reading Home.jsx...")
    with open("frontend/generated/Home.jsx", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract the JSX content (between <> and </>)
    jsx_match = re.search(r'<>\s*(.*?)\s*</>', content, re.DOTALL)
    if not jsx_match:
        print("[ERROR] Could not find JSX content")
        return
    
    jsx_content = jsx_match.group(1)
    print(f"[INFO] Original JSX content length: {len(jsx_content)} characters")
    
    # Extract major sections
    print("[INFO] Extracting major sections...")
    sections = extract_major_sections(jsx_content)
    
    print(f"[INFO] Found {len(sections)} sections:")
    for name in sections.keys():
        print(f"  - {name}: {len(sections[name])} characters")
    
    # Create components directory
    components_dir = "frontend/components"
    os.makedirs(components_dir, exist_ok=True)
    
    # Generate component files for extracted sections (except MainContent)
    component_imports = []
    
    for name, section_jsx in sections.items():
        if name == 'MainContent':
            continue
        
        component_code = create_component_file(name, section_jsx)
        component_path = f"{components_dir}/{name}.jsx"
        
        with open(component_path, "w", encoding="utf-8") as f:
            f.write(component_code)
        
        component_imports.append(f"import {name} from './components/{name}';")
        print(f"[INFO] Created {component_path} ({len(section_jsx)} chars)")
    
    # Create optimized Home.jsx with imports and component usage
    imports = '\n'.join(component_imports) if component_imports else ''
    
    # Combine components and main content
    # Maintain the original order: Topbar, ModalManager, ToastManager, LayerDestination, then MainContent
    component_order = ['Topbar', 'ModalManager', 'ToastManager', 'LayerDestination']
    ordered_usage = []
    for comp_name in component_order:
        if comp_name in sections:
            ordered_usage.append(f"      <{comp_name} />")
    
    main_content = sections.get('MainContent', '')
    # The main content should already be properly formatted JSX
    # Just ensure it's indented correctly for the return statement
    if main_content:
        # If content is on one line, try to add some basic formatting
        if '\n' not in main_content[:200]:  # Check if first 200 chars have no newlines
            # It's likely all on one line - this is fine for JSX, just indent it
            main_content = '      ' + main_content
        else:
            # Already has newlines, indent each line
            main_content_lines = main_content.split('\n')
            main_content = '\n'.join(['      ' + line if line.strip() else line for line in main_content_lines])
    
    optimized_home = f"""{imports}

export default function HomeUI() {{
  return (
    <>
{chr(10).join(ordered_usage) if ordered_usage else ''}
{main_content}
    </>
  );
}}
"""
    
    # Write optimized Home.jsx
    with open("frontend/generated/Home.jsx", "w", encoding="utf-8") as f:
        f.write(optimized_home)
    
    original_size = len(jsx_content)
    optimized_size = len(optimized_home)
    
    print(f"\n[SUCCESS] Home.jsx optimized!")
    print(f"[INFO] Original size: {original_size:,} characters")
    print(f"[INFO] Optimized size: {optimized_size:,} characters")
    print(f"[INFO] Created {len(sections) - 1} component files in {components_dir}/")

if __name__ == "__main__":
    optimize_home()
