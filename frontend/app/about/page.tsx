export default function AboutPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Navigation Bar */}
      <nav className="border-b border-gray-800 bg-black/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex-shrink-0">
              <a href="/" className="text-xl font-bold text-white hover:text-gray-300 transition-colors">
                MapSite
              </a>
            </div>
            <div className="flex space-x-8">
              <a href="/about" className="text-white px-3 py-2 rounded-md text-sm font-medium bg-gray-800/50">
                About
              </a>
              <a
                href="/contact"
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors hover:bg-gray-800/50"
              >
                Contact
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* About Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-white via-gray-300 to-gray-500 bg-clip-text text-transparent">
            About MapSite
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Building the future of location services with cutting-edge technology and innovative design.
          </p>
        </div>

        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-8 backdrop-blur-sm mb-12">
          <div className="prose prose-lg prose-invert max-w-none">
            <h2 className="text-2xl font-bold text-white mb-6">Our Mission</h2>
            <p className="text-gray-300 mb-6 leading-relaxed">
              At MapSite, we believe that location services should be fast, accurate, and beautifully designed. We're
              building the next generation of mapping technology that puts user experience first.
            </p>
            <p className="text-gray-300 mb-6 leading-relaxed">
              Our platform combines the power of Google Maps with modern web technologies to deliver lightning-fast
              performance and pixel-perfect design. Whether you're finding directions, exploring new places, or
              integrating location services into your applications, we make it simple.
            </p>
            <p className="text-gray-300 leading-relaxed">
              Founded in 2024, we're committed to pushing the boundaries of what's possible with location-based services
              while maintaining the highest standards of privacy and security.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-8 backdrop-blur-sm">
            <h3 className="text-xl font-bold text-white mb-4">Our Values</h3>
            <ul className="space-y-3 text-gray-300">
              <li className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                Innovation in mapping technology
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                User-centered design
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                Privacy and security first
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-pink-500 rounded-full mr-3"></span>
                Global accessibility
              </li>
            </ul>
          </div>

          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-8 backdrop-blur-sm">
            <h3 className="text-xl font-bold text-white mb-4">Technology Stack</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">React & Next.js</span>
                <span className="text-blue-400 text-sm">Frontend</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Google Maps API</span>
                <span className="text-green-400 text-sm">Mapping</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Tailwind CSS</span>
                <span className="text-purple-400 text-sm">Styling</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Vercel</span>
                <span className="text-pink-400 text-sm">Deployment</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
