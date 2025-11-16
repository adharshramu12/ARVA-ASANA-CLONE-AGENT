import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Asana Cloning Agent',
  description: 'Web-app cloning agent',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="w-full h-screen overflow-hidden bg-gray-50">
        <main className="w-full h-full overflow-auto">
          {children}
        </main>
      </body>
    </html>
  )
}
