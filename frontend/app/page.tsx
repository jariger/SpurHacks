"use client"

import { useState, useEffect } from "react"
import { X } from "lucide-react"
import GoogleMap from "../components/GoogleMap"
import SafetyMap from '@/components/SafetyMap'

interface MapConfig {
  api_key: string | null
  enabled: boolean
  vector_support: boolean
  default_center: {
    lat: number
    lng: number
  }
  default_zoom: number
}

export default function HomePage() {
  const [activeModal, setActiveModal] = useState<"about" | "contact" | null>(null)
  const [mapConfig, setMapConfig] = useState<MapConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null)

  // You'll need to set your Google Maps API key here
  const GOOGLE_MAPS_API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || ''

  useEffect(() => {
    // Get user's current location
    const getUserLocation = () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords
            setUserLocation({ lat: latitude, lng: longitude })
            console.log("User location obtained:", { lat: latitude, lng: longitude })
          },
          (error) => {
            console.warn("Geolocation error:", error)
            // Use default location if geolocation fails
            setUserLocation({ lat: 40.7589, lng: -73.9851 })
          },
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 300000, // 5 minutes
          },
        )
      } else {
        console.warn("Geolocation not supported")
        setUserLocation({ lat: 40.7589, lng: -73.9851 })
      }
    }

    getUserLocation()
  }, [])

  useEffect(() => {
    // Fetch map configuration from backend
    const fetchMapConfig = async () => {
      try {
        console.log("Fetching map configuration from backend...")
        const response = await fetch("http://localhost:5000/api/maps/config", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        })

        console.log("Response status:", response.status)
        console.log("Response headers:", response.headers)

        if (response.ok) {
          const config = await response.json()
          console.log("Map config received:", config)
          setMapConfig(config)
        } else {
          const errorText = await response.text()
          console.error("Backend error:", response.status, errorText)
          setError(`Failed to load map configuration: ${response.status}`)
        }
      } catch (err) {
        console.error("Network error:", err)
        setError("Backend connection failed - check if backend is running on port 5000")
      } finally {
        setLoading(false)
      }
    }

    fetchMapConfig()
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

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Navigation Bar */}
      <nav className="border-b border-gray-800 bg-black/50 backdrop-blur-xl sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo/Brand */}
            <div className="flex-shrink-0">
              <span className="text-xl font-bold text-white cursor-pointer">TrapMap</span>
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
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-16">
            <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-white via-gray-300 to-gray-500 bg-clip-text text-transparent">
              Smart mapping for smarter driving
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
              Visualize traffic ticket hotspots on the map. Plan ahead and stay informed with cutting-edge location tracking.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={scrollToMap}
                className="bg-white text-black px-6 py-3 rounded-md font-medium hover:bg-gray-200 transition-colors"
              >
                Get Started
              </button>
              <button className="border border-gray-600 text-white px-6 py-3 rounded-md font-medium hover:bg-gray-800 transition-colors">
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
        {/* Map Section */}
        <div
          id="map-section"
          className="bg-gray-900/50 rounded-xl border border-gray-800 overflow-hidden backdrop-blur-sm scroll-mt-20"
        >
          <div className="p-8 border-b border-gray-800">
            <h2 className="text-3xl font-bold text-white mb-4">Explore Your Location</h2>
            <p className="text-gray-400 text-lg">
              Interactive vector mapping powered by Google Maps. Find your current location with precision and ease.
            </p>
          </div>

          <div className="relative">
            {loading ? (
              <div className="h-[600px] bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-2 border-gray-600 border-t-white mx-auto mb-4"></div>
                  <p className="text-gray-400">
                    {userLocation ? "Loading map configuration..." : "Getting your location..."}
                  </p>
                </div>
              </div>
            ) : error ? (
              <div className="h-[600px] bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-red-400 mb-4">
                    <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                      />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">Map Error</h3>
                  <p className="text-gray-400">{error}</p>
                  <p className="text-gray-500 text-sm mt-2">Make sure your backend is running on port 5000</p>
                </div>
              </div>
            ) : mapConfig && mapConfig.api_key ? (
              <GoogleMap
                apiKey={mapConfig.api_key}
                center={userLocation || mapConfig.default_center}
                zoom={mapConfig.default_zoom}
                height="600px"
                markers={[
                  {
                    position: userLocation || mapConfig.default_center,
                    title: userLocation ? "Your Location" : "MapSite Headquarters",
                  },
                ]}
              />
            ) : (
              <div className="h-[600px] bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-yellow-400 mb-4">
                    <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                      />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">Google Maps API Key Required</h3>
                  <p className="text-gray-400">
                    Please add your Google Maps API key to the backend environment variables.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Feature Cards */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-8 backdrop-blur-sm hover:bg-gray-800/50 transition-colors">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center mb-6">
              <span className="text-white text-xl">📍</span>
            </div>
            <h3 className="text-xl font-semibold text-white mb-4">Precise Location</h3>
            <p className="text-gray-400 mb-4">
              Get exact coordinates and detailed location information with our advanced mapping technology.
            </p>
            <div className="space-y-2 text-sm text-gray-500">
              <p>📍 123 Main Street</p>
              <p>🏙️ New York, NY 10001</p>
              <p>📞 (555) 123-4567</p>
            </div>
          </div>

          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-8 backdrop-blur-sm hover:bg-gray-800/50 transition-colors">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mb-6">
              <span className="text-white text-xl">🚀</span>
            </div>
            <h3 className="text-xl font-semibold text-white mb-4">Fast Performance</h3>
            <p className="text-gray-400 mb-4">
              Lightning-fast map loading with optimized performance and smooth interactions.
            </p>
            <button className="text-blue-400 hover:text-blue-300 text-sm font-medium">Learn more →</button>
          </div>

          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-8 backdrop-blur-sm hover:bg-gray-800/50 transition-colors">
            <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center mb-6">
              <span className="text-white text-xl">🎯</span>
            </div>
            <h3 className="text-xl font-semibold text-white mb-4">Smart Navigation</h3>
            <p className="text-gray-400 mb-4">
              Intelligent routing and real-time directions to help you reach your destination efficiently.
            </p>
            <button
              onClick={scrollToMap}
              className="bg-white text-black px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-200 transition-colors"
            >
              Get Directions
            </button>
          </div>
        </div>

        {/* Stats Section */}
        <div className="mt-20 text-center">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <div className="text-3xl font-bold text-white mb-2">99.9%</div>
              <div className="text-gray-400 text-sm">Uptime</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-2">&lt; 100ms</div>
              <div className="text-gray-400 text-sm">Response Time</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-2">24/7</div>
              <div className="text-gray-400 text-sm">Support</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-2">Global</div>
              <div className="text-gray-400 text-sm">Coverage</div>
            </div>
          </div>
        </div>

        <SafetyMap apiKey={GOOGLE_MAPS_API_KEY} />
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center text-gray-400">
            <p>&copy; 2025 TrapMap. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* About Modal */}
      {activeModal === "about" && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-screen items-center justify-center p-4">
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity" onClick={closeModal} />

            {/* Modal Content */}
            <div className="relative bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
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
                    MapSite is a cutting-edge location services platform that combines the power of Google Maps API with
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
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-screen items-center justify-center p-4">
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity" onClick={closeModal} />

            {/* Modal Content */}
            <div className="relative bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full">
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
    </div>
  )
}
