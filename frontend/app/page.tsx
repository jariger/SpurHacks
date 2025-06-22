"use client"

import { useState, useEffect } from "react"
import { X } from "lucide-react"
import SafetyMap from "@/components/SafetyMap"

export default function HomePage() {
  const [activeModal, setActiveModal] = useState<"about" | "contact" | null>(null)
  const [showIntro, setShowIntro] = useState(true)
  const [introStep, setIntroStep] = useState(0)

  // You'll need to set your Google Maps API key here
  const GOOGLE_MAPS_API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || ""

  // Opening animation sequence
  useEffect(() => {
    const animationSequence = async () => {
      // Step 1: Show logo (0-1s)
      setIntroStep(1)
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Step 2: Show tagline (1-2s)
      setIntroStep(2)
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Step 3: Show loading animation (2-3s)
      setIntroStep(3)
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Step 4: Fade out intro (3-3.5s)
      setIntroStep(4)
      await new Promise((resolve) => setTimeout(resolve, 500))

      // Hide intro and show main content
      setShowIntro(false)
    }

    animationSequence()
  }, [])

  const openModal = (modal: "about" | "contact") => {
    setActiveModal(modal)
    document.body.style.overflow = "hidden"
  }

  const closeModal = () => {
    setActiveModal(null)
    document.body.style.overflow = "unset"
  }

  const scrollToMap = () => {
    const mapSection = document.getElementById("map-section")
    if (mapSection) {
      mapSection.scrollIntoView({
        behavior: "smooth",
        block: "start",
      })
    }
  }

  // Opening Animation Component
  if (showIntro) {
    return (
      <div className="fixed inset-0 bg-black flex items-center justify-center z-50 overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-900/30 via-purple-900/30 to-pink-900/30" />
          <div className="absolute inset-0">
            {/* Floating particles */}
            {[...Array(20)].map((_, i) => (
              <div
                key={i}
                className="absolute w-1 h-1 bg-white/20 rounded-full animate-pulse"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 2}s`,
                  animationDuration: `${2 + Math.random() * 3}s`,
                }}
              />
            ))}
          </div>
        </div>

        {/* Main Animation Content */}
        <div className="relative z-10 text-center">
          {/* Step 1: Logo Animation */}
          <div
            className={`transition-all duration-1000 ${
              introStep >= 1 ? "opacity-100 scale-100" : "opacity-0 scale-50"
            }`}
          >
            <div className="relative mb-8">
              <div className="w-24 h-24 mx-auto bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-2xl flex items-center justify-center transform rotate-12 hover:rotate-0 transition-transform duration-500">
                <span className="text-3xl font-bold text-white">TM</span>
              </div>
              {/* Glowing ring effect */}
              <div className="absolute inset-0 w-24 h-24 mx-auto rounded-2xl bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 opacity-20 animate-ping" />
            </div>
          </div>

          {/* Step 2: Brand Name */}
          <div
            className={`transition-all duration-1000 delay-300 ${
              introStep >= 2 ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
            }`}
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-4 bg-gradient-to-r from-white via-gray-300 to-gray-500 bg-clip-text text-transparent">
              TrapMap
            </h1>
          </div>

          {/* Step 3: Tagline */}
          <div
            className={`transition-all duration-1000 delay-500 ${
              introStep >= 2 ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
            }`}
          >
            <p className="text-xl text-gray-400 mb-8 max-w-md mx-auto">Smart mapping for smarter driving</p>
          </div>

          {/* Step 4: Loading Animation */}
          <div className={`transition-all duration-1000 delay-700 ${introStep >= 3 ? "opacity-100" : "opacity-0"}`}>
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
              <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
              <div className="w-3 h-3 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
            <p className="text-gray-500 text-sm">Initializing your experience...</p>
          </div>

          {/* Step 5: Fade out effect */}
          <div
            className={`absolute inset-0 bg-black transition-opacity duration-500 ${
              introStep >= 4 ? "opacity-100" : "opacity-0"
            }`}
          />
        </div>

        {/* Scanning line effect */}
        <div className={`absolute inset-0 ${introStep >= 3 ? "block" : "hidden"}`}>
          <div
            className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-blue-500 to-transparent animate-pulse"
            style={{
              animation: "scan 2s linear infinite",
              animationDelay: "0.5s",
            }}
          />
        </div>

        <style jsx>{`
          @keyframes scan {
            0% { top: 0%; opacity: 1; }
            50% { opacity: 1; }
            100% { top: 100%; opacity: 0; }
          }
        `}</style>
      </div>
    )
  }

  return (
    <div
      className={`min-h-screen bg-black text-white transition-all duration-1000 ${
        !showIntro ? "opacity-100" : "opacity-0"
      }`}
    >
      {/* Navigation Bar */}
      <nav className="border-b border-gray-800 bg-black/50 backdrop-blur-xl sticky top-0 z-40 animate-slideDown">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo/Brand */}
            <div className="flex-shrink-0">
              <span className="text-xl font-bold text-white cursor-pointer hover:text-blue-400 transition-colors">
                TrapMap
              </span>
            </div>

            {/* Navigation Links */}
            <div className="flex space-x-8">
              <button
                onClick={() => openModal("about")}
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors hover:bg-gray-800/50"
              >
                About
              </button>
              <button
                onClick={() => openModal("contact")}
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors hover:bg-gray-800/50"
              >
                Contact
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden animate-fadeInUp">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-16">
            <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-white via-gray-300 to-gray-500 bg-clip-text text-transparent animate-slideUp">
              Smart mapping for smarter driving
            </h1>
            <p
              className="text-xl text-gray-400 max-w-2xl mx-auto mb-8 animate-slideUp"
              style={{ animationDelay: "0.2s" }}
            >
              Visualize traffic ticket hotspots on the map. Plan ahead and stay informed with cutting-edge location
              tracking.
            </p>
            <div
              className="flex flex-col sm:flex-row gap-4 justify-center animate-slideUp"
              style={{ animationDelay: "0.4s" }}
            >
              <button
                onClick={scrollToMap}
                className="bg-white text-black px-6 py-3 rounded-md font-medium hover:bg-gray-200 transition-all duration-300 hover:scale-105 hover:shadow-lg"
              >
                Get Started
              </button>
              <button className="border border-gray-600 text-white px-6 py-3 rounded-md font-medium hover:bg-gray-800 transition-all duration-300 hover:scale-105">
                Learn More
              </button>
            </div>
          </div>

          {/* Gradient Background */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-pink-900/20 pointer-events-none" />
        </div>
      </section>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Safety Map Section */}
        <div
          id="map-section"
          className="bg-gray-900/50 rounded-xl border border-gray-800 overflow-hidden backdrop-blur-sm scroll-mt-20 animate-fadeInUp"
          style={{ animationDelay: "0.6s" }}
        >
          <div className="animate-fadeInUp" style={{ animationDelay: "1.6s" }}>
            <SafetyMap apiKey={GOOGLE_MAPS_API_KEY} />
          </div>
        </div>

        {/* Feature Cards */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              icon: "📍",
              title: "Precise Location",
              description:
                "Get exact coordinates and detailed location information with our advanced mapping technology.",
              gradient: "from-blue-500 to-cyan-500",
              delay: "0.8s",
            },
            {
              icon: "🚀",
              title: "Fast Performance",
              description: "Lightning-fast map loading with optimized performance and smooth interactions.",
              gradient: "from-purple-500 to-pink-500",
              delay: "1.0s",
            },
            {
              icon: "🎯",
              title: "Smart Navigation",
              description:
                "Intelligent routing and real-time directions to help you reach your destination efficiently.",
              gradient: "from-green-500 to-emerald-500",
              delay: "1.2s",
            },
          ].map((card, index) => (
            <div
              key={index}
              className="bg-gray-900/50 border border-gray-800 rounded-xl p-8 backdrop-blur-sm hover:bg-gray-800/50 transition-all duration-300 hover:scale-105 hover:shadow-xl animate-fadeInUp"
              style={{ animationDelay: card.delay }}
            >
              <div
                className={`w-12 h-12 bg-gradient-to-r ${card.gradient} rounded-lg flex items-center justify-center mb-6`}
              >
                <span className="text-white text-xl">{card.icon}</span>
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">{card.title}</h3>
              <p className="text-gray-400 mb-4">{card.description}</p>
              {index === 2 && (
                <button
                  onClick={scrollToMap}
                  className="bg-white text-black px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-200 transition-all duration-300 hover:scale-105"
                >
                  Get Directions
                </button>
              )}
              {index === 1 && (
                <button className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors">
                  Learn more →
                </button>
              )}
            </div>
          ))}
        </div>

        {/* Stats Section */}
        <div className="mt-20 text-center animate-fadeInUp" style={{ animationDelay: "1.4s" }}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { value: "99.9%", label: "Uptime" },
              { value: "< 100ms", label: "Response Time" },
              { value: "24/7", label: "Support" },
              { value: "Global", label: "Coverage" },
            ].map((stat, index) => (
              <div key={index} className="hover:scale-110 transition-transform duration-300">
                <div className="text-3xl font-bold text-white mb-2">{stat.value}</div>
                <div className="text-gray-400 text-sm">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-20 animate-fadeInUp" style={{ animationDelay: "1.8s" }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center text-gray-400">
            <p>&copy; 2025 TrapMap. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* About Modal */}
      {activeModal === "about" && (
        <div className="fixed inset-0 z-50 overflow-y-auto animate-fadeIn">
          <div className="flex min-h-screen items-center justify-center p-4">
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity" onClick={closeModal} />

            {/* Modal Content */}
            <div className="relative bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto animate-slideUp">
              {/* Modal Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-800">
                <h2 className="text-2xl font-bold bg-gradient-to-r from-white via-gray-300 to-gray-500 bg-clip-text text-transparent">
                  About TrapMap
                </h2>
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-gray-800 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Modal Body */}
              <div className="p-6">
                <div className="prose prose-invert max-w-none">
                  <p className="text-gray-300 mb-6">
                    TrapMap is a cutting-edge location services platform that combines the power of Google Maps API with
                    modern web technologies to deliver an exceptional user experience.
                  </p>

                  <h3 className="text-xl font-semibold text-white mb-4">Features</h3>
                  <ul className="text-gray-300 space-y-2 mb-6">
                    <li>• Vector-based map rendering for crisp, scalable graphics</li>
                    <li>• Real-time geocoding and reverse geocoding</li>
                    <li>• Advanced place search and discovery</li>
                    <li>• Interactive directions and routing</li>
                    <li>• Custom map styling and theming</li>
                    <li>• Responsive design for all devices</li>
                  </ul>

                  <h3 className="text-xl font-semibold text-white mb-4">Technology Stack</h3>
                  <ul className="text-gray-300 space-y-2">
                    <li>• Frontend: Next.js 15, React 18, TypeScript</li>
                    <li>• Backend: Flask, Python</li>
                    <li>• Maps: Google Maps JavaScript API</li>
                    <li>• Styling: Tailwind CSS</li>
                    <li>• UI Components: Radix UI</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Contact Modal */}
      {activeModal === "contact" && (
        <div className="fixed inset-0 z-50 overflow-y-auto animate-fadeIn">
          <div className="flex min-h-screen items-center justify-center p-4">
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity" onClick={closeModal} />

            {/* Modal Content */}
            <div className="relative bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full animate-slideUp">
              {/* Modal Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-800">
                <h2 className="text-2xl font-bold bg-gradient-to-r from-white via-gray-300 to-gray-500 bg-clip-text text-transparent">
                  Contact Us
                </h2>
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-gray-800 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Modal Body */}
              <div className="p-6">
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-2">Get in Touch</h3>
                    <p className="text-gray-300">
                      Have questions about our mapping services? We'd love to hear from you.
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                        <span className="text-white text-sm">📧</span>
                      </div>
                      <div>
                        <p className="text-white font-medium">Email</p>
                        <p className="text-gray-400">contact@TrapMap.com</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                        <span className="text-white text-sm">📞</span>
                      </div>
                      <div>
                        <p className="text-white font-medium">Phone</p>
                        <p className="text-gray-400">+1 (555) 123-4567</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center">
                        <span className="text-white text-sm">📍</span>
                      </div>
                      <div>
                        <p className="text-white font-medium">Address</p>
                        <p className="text-gray-400">123 Main Street, New York, NY 10001</p>
                      </div>
                    </div>
                  </div>

                  <div className="pt-4 border-t border-gray-800">
                    <p className="text-gray-400 text-sm">
                      Our support team is available 24/7 to assist you with any questions or concerns.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Custom CSS for animations */}
      <style jsx global>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        @keyframes fadeInUp {
          from { 
            opacity: 0; 
            transform: translateY(30px); 
          }
          to { 
            opacity: 1; 
            transform: translateY(0); 
          }
        }
        
        @keyframes slideUp {
          from { 
            opacity: 0; 
            transform: translateY(50px); 
          }
          to { 
            opacity: 1; 
            transform: translateY(0); 
          }
        }
        
        @keyframes slideDown {
          from { 
            opacity: 0; 
            transform: translateY(-30px); 
          }
          to { 
            opacity: 1; 
            transform: translateY(0); 
          }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }
        
        .animate-fadeInUp {
          animation: fadeInUp 0.8s ease-out both;
        }
        
        .animate-slideUp {
          animation: slideUp 0.8s ease-out both;
        }
        
        .animate-slideDown {
          animation: slideDown 0.6s ease-out both;
        }
      `}</style>
    </div>
  )
}
