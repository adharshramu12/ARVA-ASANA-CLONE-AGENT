export function sanitizeHtml(html: string | null | undefined): string {
  if (!html) return "";

  let out = html;

  // 1) Neutralize absolute Asana links: keep the URL but stop real navigation.
  //    Example: href="https://app.asana.com/..." becomes:
  //    href="#" data-asana-url="https://app.asana.com/..."
  out = out.replace(
    /href="https?:\/\/(?:app\.asana\.com|asana\.com)[^"]*"/g,
    (match) => {
      const urlMatch = match.match(/href="([^"]+)"/);
      const url = urlMatch ? urlMatch[1] : "#";
      return `href="#" data-asana-url="${url}"`;
    }
  );

  // 2) Remove javascript: URLs entirely for safety.
  out = out.replace(/href="javascript:[^"]*"/gi, `href="#"`);

  // 3) Neutralize form actions pointing to Asana (we don't want to submit to them).
  out = out.replace(
    /action="https?:\/\/(?:app\.asana\.com|asana\.com)[^"]*"/g,
    `action="#"`
  );

  // 4) Remove broken HTML fragments that create garbage text
  //    Remove any raw text starting with ass=" or containing orphan attributes
  out = out.replace(/ass="[^"]*"/g, "");
  out = out.replace(/\bass=["'][^"']*["']/g, "");
  
  // 5) Remove problematic class patterns that appear as text nodes
  const problematicPatterns = [
    /ThemeableCardPresentation--isValid/g,
    /ThemeableCardPresentation(?!\w)/g,
    /CalloutCard/g,
    /TrialCalloutCard/g,
    /HighlightSol--buildingBlock/g,
    /HighlightSol(?!\w)/g,
    /Stack--display-block/g,
    /Stack--direction-column/g
  ];
  
  problematicPatterns.forEach(pattern => {
    out = out.replace(pattern, "");
  });

  // 6) Remove any full-screen loading overlays that may block scroll.
  //    Remove elements with these classes: loading-screen, spinner, overlay, blocking-layer
  out = out.replace(
    /<div[^>]+class="[^"]*(?:loading-screen|spinner|overlay|blocking-layer)[^"]*"[\s\S]*?<\/div>/gi,
    ""
  );
  out = out.replace(
    /<div[^>]+class="[^"]*[^"]*(?:loading-screen|spinner|overlay|blocking-layer)[^"]*"[\s\S]*?<\/div>/gi,
    ""
  );

  // 7) Remove invisible blocking overlays and problematic wrapper classes
  const removeClasses = [
    'overlay',
    'intercept-layer',
    'ThemeableCardPresentation--isValid',
    'stack-root',
    'portal-layer'
  ];
  
  removeClasses.forEach(className => {
    const regex = new RegExp(`<div[^>]+class="[^"]*\\b${className}\\b[^"]*"[^>]*>([\\s\\S]*?)<\\/div>`, 'gi');
    out = out.replace(regex, '$1'); // Keep inner content, remove wrapper
  });

  // 8) Clean up any malformed HTML attributes or orphan text nodes
  out = out.replace(/\s+class=""\s*/g, ' ');
  out = out.replace(/\s+style=""\s*/g, ' ');
  out = out.replace(/\s{2,}/g, ' ');

  return out;
}

