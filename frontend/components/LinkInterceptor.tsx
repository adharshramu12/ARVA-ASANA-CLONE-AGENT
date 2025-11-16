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
          
          // Block all external Asana links
          if (href && (href.startsWith("https://app.asana.com") || href.startsWith("https://asana.com"))) {
            e.preventDefault();
            e.stopPropagation();
            console.log("Blocked external Asana link:", href);
            return;
          }
          
          // Handle navigation links with data-asana-url attribute
          if (asanaUrl) {
            e.preventDefault();
            e.stopPropagation();
            
            // Route to internal pages based on Asana URL patterns
            if (asanaUrl.includes('/0/home') || asanaUrl.includes('/home')) {
              router.push('/');
              return;
            } else if (asanaUrl.includes('/0/projects') || asanaUrl.includes('/projects')) {
              router.push('/projects');
              return;
            } else if (asanaUrl.includes('/0/mytasks') || asanaUrl.includes('/mytasks') || asanaUrl.includes('/tasks')) {
              router.push('/tasks');
              return;
            }
            
            // Block all other external Asana links
            console.log("Blocked external link:", asanaUrl);
            return;
          }
          
          // Handle internal routing
          if (href && href.startsWith("/")) {
            e.preventDefault();
            e.stopPropagation();
            router.push(href);
            return;
          }
          
          // Block all other external links
          if (href && (href.startsWith("http://") || href.startsWith("https://"))) {
            e.preventDefault();
            e.stopPropagation();
            console.log("Blocked external link:", href);
            return;
          }
        }
      }}
    >
      {children}
    </div>
  );
}

