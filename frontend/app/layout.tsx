import type { Metadata } from 'next'
import './globals.css'
import LinkInterceptor from '@/components/LinkInterceptor'
import { DropdownProvider, DropdownManager } from '@/components/DropdownManager'

export const metadata: Metadata = {
  title: 'Asana Clone',
  description: 'Pixel-perfect Asana clone built with Next.js',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        {/* Load Asana's original CSS for pixel-perfect styling */}
        <link 
          type="text/css" 
          rel="stylesheet" 
          href="https://d3ki9tyy5l5ruj.cloudfront.net/compressed/build/bundles/aaae54decd19e50b9399d07e500a39ff29f49037/apps/asana/css/themes/root.css"
        />
      </head>
      <body className="w-full h-screen overflow-hidden bg-[#F7F7F7]">
        <DropdownProvider>
          <main className="w-full h-full overflow-auto">
            <DropdownManager>
              <LinkInterceptor>
                {children}
              </LinkInterceptor>
            </DropdownManager>
          </main>
        </DropdownProvider>
      </body>
    </html>
  )
}
