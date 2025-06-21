import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'TrapMap',
  description: 'Created with v0',
  generator: 'v0.dev',
  icons: {
    icon: '/Trap_Man.png',  // Replace with your actual filename
  }
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
