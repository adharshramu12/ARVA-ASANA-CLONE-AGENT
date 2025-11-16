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

  // 4) Remove any full-screen loading overlays that may block scroll.
  //    Remove elements with these classes: loading-screen, spinner, overlay, blocking-layer
  out = out.replace(
    /<div[^>]+class="[^"]*(?:loading-screen|spinner|overlay|blocking-layer)[^"]*"[\s\S]*?<\/div>/gi,
    ""
  );
  out = out.replace(
    /<div[^>]+class="[^"]*[^"]*(?:loading-screen|spinner|overlay|blocking-layer)[^"]*"[\s\S]*?<\/div>/gi,
    ""
  );

  return out;
}

