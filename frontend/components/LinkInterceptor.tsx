'use client';

import { useRouter } from "next/navigation";
import { ReactNode } from "react";

export default function LinkInterceptor({ children }: { children: ReactNode }) {
  const router = useRouter();

  return (
    <div
      onClick={(e: React.MouseEvent<HTMLDivElement>) => {
        const link = (e.target as HTMLElement).closest("a");
        if (link) {
          const href = link.getAttribute("href");
          const asanaUrl = link.getAttribute("data-asana-url");
          
          // Block all external Asana links completely
          if (href && (href.startsWith("https://app.asana.com") || href.startsWith("https://asana.com"))) {
            e.preventDefault();
            e.stopPropagation();
            console.log("🚫 Blocked external Asana link:", href);
            return;
          }
          
          // Handle navigation links with data-asana-url attribute
          if (asanaUrl) {
            e.preventDefault();
            e.stopPropagation();
            
            // Route to internal pages based on Asana URL patterns
            if (asanaUrl.includes('/0/home') || asanaUrl.includes('/home')) {
              console.log("🏠 Routing to Home");
              router.push('/');
              return;
            } else if (asanaUrl.includes('/0/projects') || asanaUrl.includes('/projects')) {
              console.log("📁 Routing to Projects");
              router.push('/projects');
              return;
            } else if (asanaUrl.includes('/0/mytasks') || asanaUrl.includes('/mytasks') || asanaUrl.includes('/tasks')) {
              console.log("✅ Routing to Tasks");
              router.push('/tasks');
              return;
            }
            
            // Block all other external Asana links
            console.log("🚫 Blocked external Asana link:", asanaUrl);
            return;
          }
          
          // Handle internal routing for relative paths
          if (href && href.startsWith("/")) {
            // Check if it contains keywords for internal routing
            if (href.includes('projects') || href.toLowerCase().includes('project')) {
              e.preventDefault();
              e.stopPropagation();
              console.log("📁 Routing to Projects");
              router.push('/projects');
              return;
            } else if (href.includes('tasks') || href.includes('mytasks')) {
              e.preventDefault();
              e.stopPropagation();
              console.log("✅ Routing to Tasks");
              router.push('/tasks');
              return;
            } else if (href.includes('home') || href === '/') {
              e.preventDefault();
              e.stopPropagation();
              console.log("🏠 Routing to Home");
              router.push('/');
              return;
            }
            
            // For other internal paths, navigate normally
            e.preventDefault();
            e.stopPropagation();
            router.push(href);
            return;
          }
          
          // Block ALL other external links (http/https)
          if (href && (href.startsWith("http://") || href.startsWith("https://"))) {
            e.preventDefault();
            e.stopPropagation();
            console.log("🚫 Blocked external link:", href);
            return;
          }
          
          // Block # links (anchors without proper href)
          if (href === "#" || !href) {
            e.preventDefault();
            e.stopPropagation();
            return;
          }
        }
      }}
    >
      {children}
    </div>
  );
}

