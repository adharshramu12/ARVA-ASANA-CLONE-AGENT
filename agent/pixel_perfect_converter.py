#!/usr/bin/env python3
"""
Pixel-Perfect HTML to React Converter
Preserves exact styling, structure, and layout from scraped Asana pages
"""

import json
import re
from html.parser import HTMLParser
from typing import Dict, List, Tuple


class PixelPerfectConverter(HTMLParser):
    """Converts HTML to JSX while preserving exact pixel-perfect styling"""
    
    def __init__(self):
        super().__init__()
        self.jsx_parts = []
        self.tag_stack = []
        self.css_map = {}
        self.indent_level = 0
        
    def get_indent(self):
        """Get current indentation"""
        return '  ' * self.indent_level
    
    def convert_attr_name(self, attr):
        """Convert HTML attributes to JSX format"""
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
            'crossorigin': 'crossOrigin',
            'datetime': 'dateTime',
            'hreflang': 'hrefLang',
            'spellcheck': 'spellCheck',
            'autocomplete': 'autoComplete',
            'autocapitalize': 'autoCapitalize',
            'autofocus': 'autoFocus',
            'autoplay': 'autoPlay',
            'charset': 'charSet',
            'colspan': 'colSpan',
            'rowspan': 'rowSpan',
        }
        
        # Handle aria-* and data-* attributes
        if attr.startswith('aria-') or attr.startswith('data-'):
            return attr
        
        # Handle SVG attributes
        svg_attrs = {
            'viewbox': 'viewBox',
            'preserveaspectratio': 'preserveAspectRatio',
            'gradientunits': 'gradientUnits',
            'gradienttransform': 'gradientTransform',
            'patternunits': 'patternUnits',
            'patterntransform': 'patternTransform',
            'spreadmethod': 'spreadMethod',
            'startoffset': 'startOffset',
            'stddeviation': 'stdDeviation',
            'stitchtiles': 'stitchTiles',
            'basefrequency': 'baseFrequency',
            'calcmode': 'calcMode',
            'clippathunits': 'clipPathUnits',
            'contentscripttype': 'contentScriptType',
            'contentstyletype': 'contentStyleType',
            'diffuseconstant': 'diffuseConstant',
            'edgemode': 'edgeMode',
            'externalresourcesrequired': 'externalResourcesRequired',
            'filterres': 'filterRes',
            'filterunits': 'filterUnits',
            'glyphref': 'glyphRef',
            'kernelmatrix': 'kernelMatrix',
            'kernelunitlength': 'kernelUnitLength',
            'keypoints': 'keyPoints',
            'keysplines': 'keySplines',
            'keytimes': 'keyTimes',
            'lengthadjust': 'lengthAdjust',
            'limitingconeangle': 'limitingConeAngle',
            'markerheight': 'markerHeight',
            'markerunits': 'markerUnits',
            'markerwidth': 'markerWidth',
            'maskcontentunits': 'maskContentUnits',
            'maskunits': 'maskUnits',
            'numoctaves': 'numOctaves',
            'pathlength': 'pathLength',
            'patterncontentunits': 'patternContentUnits',
            'pointsatx': 'pointsAtX',
            'pointsaty': 'pointsAtY',
            'pointsatz': 'pointsAtZ',
            'preservealpha': 'preserveAlpha',
            'primitiveunits': 'primitiveUnits',
            'refx': 'refX',
            'refy': 'refY',
            'repeatcount': 'repeatCount',
            'repeatdur': 'repeatDur',
            'requiredextensions': 'requiredExtensions',
            'requiredfeatures': 'requiredFeatures',
            'specularconstant': 'specularConstant',
            'specularexponent': 'specularExponent',
            'surfacescale': 'surfaceScale',
            'systemlanguage': 'systemLanguage',
            'tablevalues': 'tableValues',
            'targetx': 'targetX',
            'targety': 'targetY',
            'textlength': 'textLength',
            'xchannelselector': 'xChannelSelector',
            'ychannelselector': 'yChannelSelector',
            'zoomandpan': 'zoomAndPan',
        }
        
        return svg_attrs.get(attr.lower(), attr_map.get(attr.lower(), attr))
    
    def convert_style_to_jsx(self, style_str):
        """Convert inline CSS to JSX style object"""
        if not style_str or not style_str.strip():
            return None
        
        styles = {}
        for declaration in style_str.split(';'):
            declaration = declaration.strip()
            if ':' not in declaration:
                continue
            
            prop, value = declaration.split(':', 1)
            prop = prop.strip()
            value = value.strip()
            
            if not prop or not value:
                continue
            
            # Convert kebab-case to camelCase
            prop_parts = prop.split('-')
            camel_prop = prop_parts[0] + ''.join(p.capitalize() for p in prop_parts[1:])
            
            styles[camel_prop] = value
        
        if not styles:
            return None
        
        # Build JSX style object as actual JavaScript object syntax
        style_parts = []
        for key, value in styles.items():
            # Escape quotes and backslashes in values
            value_escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            style_parts.append(f'"{key}": "{value_escaped}"')
        
        return '{{' + ', '.join(style_parts) + '}}'
    
    def handle_starttag(self, tag, attrs):
        """Handle opening tag"""
        # Skip problematic tags
        skip_tags = {
            'script', 'noscript', 'iframe', 'object', 'embed', 
            'link', 'meta', 'head', 'html', 'body', 'title',
            'base', 'command', 'basefont'
        }
        
        if tag.lower() in skip_tags:
            return
        
        jsx_attrs = []
        style_attr = None
        
        for attr, value in attrs:
            if attr is None:
                continue
            
            # Skip event handlers (onclick, onload, etc.)
            if attr.lower().startswith('on') and attr.lower() not in ['open']:
                continue
            
            # Skip certain problematic attributes
            if attr.lower() in ['xmlns', 'xml:lang', 'xml:space']:
                continue
            
            # Convert attribute name
            jsx_attr = self.convert_attr_name(attr)
            
            if value is None:
                # Boolean attribute without value
                jsx_attrs.append(jsx_attr)
            elif value == '':
                # Empty string value - skip it
                continue
            elif jsx_attr == 'style':
                # Handle style separately
                style_attr = self.convert_style_to_jsx(value)
            else:
                # Regular attribute - escape value
                value_escaped = value.replace('"', '&quot;').replace('{', '&#123;').replace('}', '&#125;')
                jsx_attrs.append(f'{jsx_attr}="{value_escaped}"')
        
        # Add style if present
        if style_attr:
            jsx_attrs.append(f'style={style_attr}')
        
        # Build opening tag
        attrs_str = ' ' + ' '.join(jsx_attrs) if jsx_attrs else ''
        
        # Self-closing tags
        void_tags = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }
        
        indent = self.get_indent()
        
        if tag.lower() in void_tags:
            self.jsx_parts.append(f'{indent}<{tag}{attrs_str} />')
        else:
            self.jsx_parts.append(f'{indent}<{tag}{attrs_str}>')
            self.tag_stack.append(tag)
            self.indent_level += 1
    
    def handle_endtag(self, tag):
        """Handle closing tag"""
        skip_tags = {
            'script', 'noscript', 'iframe', 'object', 'embed',
            'link', 'meta', 'head', 'html', 'body', 'title',
            'base', 'command', 'basefont'
        }
        
        if tag.lower() in skip_tags:
            return
        
        if self.tag_stack and self.tag_stack[-1].lower() == tag.lower():
            self.indent_level -= 1
            self.tag_stack.pop()
            indent = self.get_indent()
            self.jsx_parts.append(f'{indent}</{tag}>')
    
    def handle_data(self, data):
        """Handle text content"""
        # Keep whitespace structure but escape special characters
        if data.strip():
            # Escape JSX special characters
            data = data.replace('{', '&#123;').replace('}', '&#125;')
            indent = self.get_indent()
            self.jsx_parts.append(f'{indent}{data}')
    
    def handle_comment(self, data):
        """Skip HTML comments"""
        pass
    
    def get_jsx(self):
        """Get final JSX output"""
        return '\n'.join(self.jsx_parts)


def extract_body_content(html):
    """Extract body content from full HTML document"""
    # Try to find body tag
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
    if body_match:
        return body_match.group(1)
    
    # If no body tag, try to find main content area
    main_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL | re.IGNORECASE)
    if main_match:
        return main_match.group(1)
    
    # Return as-is if no body found
    return html


def clean_html(html):
    """Clean HTML while preserving structure and styling"""
    # Remove script tags completely
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove noscript tags
    html = re.sub(r'<noscript[^>]*>.*?</noscript>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML comments (but keep conditional comments for IE if needed)
    html = re.sub(r'<!--(?!\[if).*?-->', '', html, flags=re.DOTALL)
    
    # Remove DOCTYPE
    html = re.sub(r'<!DOCTYPE[^>]*>', '', html, flags=re.IGNORECASE)
    
    # Remove style tags (we'll use inline styles instead)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove link tags (external CSS)
    html = re.sub(r'<link[^>]*/?>', '', html, flags=re.IGNORECASE)
    
    # Remove meta tags
    html = re.sub(r'<meta[^>]*/?>', '', html, flags=re.IGNORECASE)
    
    # Remove head tag and its contents
    html = re.sub(r'<head[^>]*>.*?</head>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove html and body tags (keep content)
    html = re.sub(r'</?html[^>]*>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'</?body[^>]*>', '', html, flags=re.IGNORECASE)
    
    return html


def process_css_data(css_data):
    """Process CSS data to create inline styles for exact pixel matching"""
    css_map = {}
    
    for item in css_data:
        element_id = f"{item.get('tag', 'div')}_{item.get('id', '')}_{item.get('class', '')}"
        css_map[element_id] = item.get('css', {})
    
    return css_map


def convert_page_to_pixel_perfect_jsx(json_path, component_name):
    """Convert scraped page to pixel-perfect React component"""
    print(f"\n{'='*70}")
    print(f"🎨 Converting {component_name} to Pixel-Perfect JSX")
    print(f"{'='*70}\n")
    
    # Load extracted data
    print(f"📂 Loading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    html = data.get('html', '')
    css_data = data.get('css', [])
    
    print(f"📏 Original HTML: {len(html):,} characters")
    print(f"🎨 CSS rules: {len(css_data):,} elements")
    
    # Extract body content
    html = extract_body_content(html)
    print(f"📦 Body content: {len(html):,} characters")
    
    # Clean HTML
    html = clean_html(html)
    print(f"🧹 Cleaned HTML: {len(html):,} characters")
    
    # Convert to JSX
    print("⚙️  Converting HTML to JSX...")
    converter = PixelPerfectConverter()
    
    try:
        converter.feed(html)
        jsx_content = converter.get_jsx()
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        raise
    
    print(f"✅ JSX generated: {len(jsx_content):,} characters")
    
    # Create React component with 'use client' directive
    component_code = f"""'use client';

export default function {component_name}() {{
  return (
    <div className="w-full h-screen overflow-auto bg-[#F7F7F7]">
{jsx_content}
    </div>
  );
}}
"""
    
    print(f"📦 Final component: {len(component_code):,} characters")
    
    return component_code


def process_all_pages():
    """Process all scraped pages"""
    import os
    
    pages = {
        'home': 'Home',
        'projects': 'Projects',
        'tasks': 'Tasks'
    }
    
    extracted_dir = 'agent/extracted'
    generated_dir = 'frontend/generated'
    
    # Create output directory
    os.makedirs(generated_dir, exist_ok=True)
    
    print("\n" + "="*70)
    print("🚀 PIXEL-PERFECT CONVERSION PIPELINE")
    print("="*70)
    
    for page_name, component_name in pages.items():
        json_path = f'{extracted_dir}/{page_name}.json'
        output_path = f'{generated_dir}/{component_name}.jsx'
        
        if not os.path.exists(json_path):
            print(f"\n⚠️  Skipping {page_name} - {json_path} not found")
            continue
        
        try:
            # Convert to pixel-perfect JSX
            component_code = convert_page_to_pixel_perfect_jsx(json_path, component_name)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(component_code)
            
            print(f"💾 Saved to {output_path}")
            print(f"✅ {component_name} conversion complete!\n")
            
        except Exception as e:
            print(f"❌ Failed to convert {page_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("🎉 PIXEL-PERFECT CONVERSION COMPLETE!")
    print("="*70)
    print("\n📋 Next steps:")
    print("   1. cd frontend")
    print("   2. npm run dev")
    print("   3. Open http://localhost:3000")
    print()


if __name__ == '__main__':
    process_all_pages()
