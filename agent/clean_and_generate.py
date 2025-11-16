#!/usr/bin/env python3
"""
Clean and Generate - Comprehensive HTML Cleaner and JSX Generator
This script removes ALL garbage from scraped Asana HTML and generates clean React components.
"""

import re
import json
from pathlib import Path


def remove_garbage_patterns(html):
    """Remove all garbage patterns from HTML"""
    print("🧹 Removing garbage patterns...")
    
    # Remove problematic class/attribute fragments
    garbage_patterns = [
        r'ass="[^"]*"',  # ass=" garbage
        r'aria[A-Z][a-zA-Z]*="[^"]*"',  # ariaHidden, ariaLabel (use aria-hidden instead)
        r'data[A-Z][a-zA-Z]*="[^"]*"',  # dataTestid (use data-testid instead)
        r'\bHighlightSol[^"\s]*',  # HighlightSol classes
        r'\bThemeableCardPresentation[^"\s]*',  # ThemeableCardPresentation classes
        r'\bStack--[^"\s]*',  # Stack-- utility classes
        r'\bTypographyPresentation[^"\s]*',  # TypographyPresentation classes
        r'\bButtonThemeablePresentation[^"\s]*',  # ButtonThemeablePresentation classes
        r'\bItemRow[^"\s]*',  # ItemRow classes
        r'\bPillThemeablePresentation[^"\s]*',  # PillThemeablePresentation classes
        r'\bSpreadsheet[^"\s]*',  # Spreadsheet classes
        r'\bFloatingToolbar[^"\s]*',  # FloatingToolbar classes
        r'\bSortableList[^"\s]*',  # SortableList classes
        r'\bCustomizableHomePage[^"\s]*',  # CustomizableHomePage classes
        r'\b--[a-z-]+:\s*[^;]+;',  # CSS variables like --size: 26px;
    ]
    
    for pattern in garbage_patterns:
        html = re.sub(pattern, '', html, flags=re.IGNORECASE)
    
    # Remove empty class attributes
    html = re.sub(r'\s+class=""', '', html)
    html = re.sub(r'\s+className=""', '', html)
    
    # Clean up excessive whitespace
    html = re.sub(r'\s+', ' ', html)
    html = re.sub(r'>\s+<', '><', html)
    
    return html


def fix_attributes(html):
    """Fix HTML attributes to JSX format"""
    print("🔧 Fixing attributes...")
    
    # Convert class to className
    html = re.sub(r'\bclass=', 'className=', html, flags=re.IGNORECASE)
    
    # Convert aria-* attributes (kebab to camel)
    aria_attrs = {
        'aria-label': 'ariaLabel',
        'aria-hidden': 'ariaHidden',
        'aria-expanded': 'ariaExpanded',
        'aria-haspopup': 'ariaHaspopup',
        'aria-selected': 'ariaSelected',
        'aria-pressed': 'ariaPressed',
        'aria-disabled': 'ariaDisabled',
        'aria-controls': 'ariaControls',
        'aria-describedby': 'ariaDescribedby',
        'aria-labelledby': 'ariaLabelledby',
        'aria-valuenow': 'ariaValuenow',
        'aria-valuemin': 'ariaValuemin',
        'aria-valuemax': 'ariaValuemax',
        'aria-orientation': 'ariaOrientation',
        'aria-live': 'ariaLive',
        'aria-autocomplete': 'ariaAutocomplete',
    }
    
    for old_attr, new_attr in aria_attrs.items():
        html = re.sub(rf'\b{old_attr}=', f'{new_attr}=', html, flags=re.IGNORECASE)
    
    # Convert data-* attributes (kebab to camel)
    data_attrs = {
        'data-testid': 'dataTestid',
        'data-test-id': 'dataTestid',
        'data-command': 'dataCommand',
        'data-carousel-item-key': 'dataCarouselItemKey',
        'data-task-id': 'dataTaskId',
        'data-active-item': 'dataActiveItem',
    }
    
    for old_attr, new_attr in data_attrs.items():
        html = re.sub(rf'\b{old_attr}=', f'{new_attr}=', html, flags=re.IGNORECASE)
    
    # Convert other HTML-only attributes
    other_attrs = {
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
        'autocomplete': 'autoComplete',
        'for': 'htmlFor',
        'crossorigin': 'crossOrigin',
        'novalidate': 'noValidate',
    }
    
    for old_attr, new_attr in other_attrs.items():
        html = re.sub(rf'\b{old_attr}=', f'{new_attr}=', html, flags=re.IGNORECASE)
    
    return html


def fix_svg_attributes(html):
    """Fix SVG-specific attributes"""
    print("🎨 Fixing SVG attributes...")
    
    svg_attrs = {
        'viewbox': 'viewBox',
        'gradientunits': 'gradientUnits',
        'gradienttransform': 'gradientTransform',
        'patternunits': 'patternUnits',
        'patterntransform': 'patternTransform',
        'clippath': 'clipPath',
        'fillrule': 'fillRule',
        'strokedasharray': 'strokeDasharray',
        'strokedashoffset': 'strokeDashoffset',
        'strokelinecap': 'strokeLinecap',
        'strokelinejoin': 'strokeLinejoin',
        'strokemiterlimit': 'strokeMiterlimit',
        'strokewidth': 'strokeWidth',
        'textanchor': 'textAnchor',
    }
    
    for old_attr, new_attr in svg_attrs.items():
        html = re.sub(rf'\b{old_attr}=', f'{new_attr}=', html, flags=re.IGNORECASE)
    
    return html


def remove_inline_scripts_and_styles(html):
    """Remove <script> and <style> tags"""
    print("🚫 Removing scripts and styles...")
    
    # Remove script tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove style tags
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove link stylesheets (external)
    html = re.sub(r'<link[^>]*type="text/css"[^>]*>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<link[^>]*rel="stylesheet"[^>]*>', '', html, flags=re.IGNORECASE)
    
    # Remove iframes
    html = re.sub(r'<iframe[^>]*>.*?</iframe>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    return html


def simplify_structure(html):
    """Simplify overly complex nested structures"""
    print("📦 Simplifying structure...")
    
    # Remove excessive nested divs with only classes
    html = re.sub(r'<div className="[^"]*">\s*<div className="[^"]*">\s*<div className="[^"]*">', '<div>', html)
    
    # Remove empty divs
    html = re.sub(r'<div[^>]*>\s*</div>', '', html)
    
    # Remove empty spans
    html = re.sub(r'<span[^>]*>\s*</span>', '', html)
    
    return html


def create_clean_component(page_name, cleaned_html):
    """Create a clean React component from HTML"""
    print(f"⚛️  Creating {page_name} component...")
    
    component_template = f'''export default function {page_name}() {{
  return (
    <div className="w-full h-full overflow-auto p-4 bg-[#F7F7F7]">
      {cleaned_html}
    </div>
  );
}}
'''
    
    return component_template


def process_extracted_json(json_file, output_jsx_file):
    """Process extracted JSON and generate clean JSX"""
    print(f"\n{'='*70}")
    print(f"  Processing {json_file.name}")
    print(f"{'='*70}")
    
    try:
        # Read JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        html = data.get('html', '')
        if not html:
            print("⚠️  No HTML content found in JSON")
            return False
        
        print(f"📄 Original HTML size: {len(html):,} characters")
        
        # Extract body content if present
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
        if body_match:
            html = body_match.group(1)
            print("✂️  Extracted body content")
        
        # Apply cleaning pipeline
        html = remove_inline_scripts_and_styles(html)
        html = remove_garbage_patterns(html)
        html = fix_attributes(html)
        html = fix_svg_attributes(html)
        html = simplify_structure(html)
        
        print(f"✨ Cleaned HTML size: {len(html):,} characters")
        print(f"📉 Size reduction: {((1 - len(html) / data.get('html', html).__len__()) * 100):.1f}%")
        
        # Extract page name from filename
        page_name = json_file.stem.capitalize()  # home.json -> Home
        
        # Create component
        component_code = create_clean_component(page_name, html)
        
        # Write to output file
        output_jsx_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_jsx_file, 'w', encoding='utf-8') as f:
            f.write(component_code)
        
        print(f"✅ Generated {output_jsx_file.name} successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {json_file.name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("  ASANA HTML CLEANER & JSX GENERATOR")
    print("="*70)
    
    # Setup paths
    agent_dir = Path(__file__).parent
    extracted_dir = agent_dir / 'extracted'
    frontend_dir = agent_dir.parent / 'frontend'
    generated_dir = frontend_dir / 'generated'
    
    # Check if extracted directory exists
    if not extracted_dir.exists():
        print(f"❌ Extracted directory not found: {extracted_dir}")
        print("   Please run the scraper first to generate extracted JSON files.")
        return False
    
    # Process each JSON file
    pages = ['home', 'projects', 'tasks']
    results = {}
    
    for page in pages:
        json_file = extracted_dir / f'{page}.json'
        jsx_file = generated_dir / f'{page.capitalize()}.jsx'
        
        if not json_file.exists():
            print(f"\n⚠️  Skipping {page}: JSON file not found")
            results[page] = False
            continue
        
        results[page] = process_extracted_json(json_file, jsx_file)
    
    # Print summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    
    for page, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}  {page.capitalize()}.jsx")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    print(f"\n📊 {passed}/{total} components generated successfully")
    
    if passed == total:
        print("\n🎉 All components generated! Ready to test.")
        print("\n🚀 Next steps:")
        print("   cd frontend")
        print("   npm run dev")
    else:
        print("\n⚠️  Some components failed to generate. Check errors above.")
    
    return passed == total


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
