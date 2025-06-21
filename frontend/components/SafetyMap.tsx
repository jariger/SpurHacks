"use client"

import { useEffect, useState } from 'react'
import GoogleMap from './GoogleMap'

interface SafetyMarker {
  position: { lat: number; lng: number }
  title: string
  icon: string
  location: string
  safety_score: number
  safety_level: string
  recommendations: string[]
  infraction_count: number
  details: {
    reasoning: string[]
    has_street_parking: boolean
    nearby_lots: number
  }
}

interface SafetyMapProps {
  apiKey: string
}

export default function SafetyMap({ apiKey }: SafetyMapProps) {
  const [markers, setMarkers] = useState<SafetyMarker[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedMarker, setSelectedMarker] = useState<SafetyMarker | null>(null)
  const [map, setMap] = useState<google.maps.Map | null>(null)
  const [infoWindow, setInfoWindow] = useState<google.maps.InfoWindow | null>(null)

  useEffect(() => {
    console.log('🔄 Fetching safety data from backend...')
    fetchSafetyData()
  }, [])

  const fetchSafetyData = async () => {
    try {
      console.log('🔄 Fetching safety data from backend...')
      const response = await fetch('http://localhost:5000/api/safety-markers')
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data.error) {
        throw new Error(data.error)
      }
      
      console.log(`✅ Loaded ${data.markers.length} safety markers`)
      setMarkers(data.markers)
      setLoading(false)
      
    } catch (err) {
      console.error('❌ Error fetching safety data:', err)
      setError(err instanceof Error ? err.message : 'Failed to load safety data')
      setLoading(false)
    }
  }

  const handleMapLoad = (mapInstance: google.maps.Map) => {
    setMap(mapInstance)
    
    // Create info window
    const infoWindowInstance = new google.maps.InfoWindow()
    setInfoWindow(infoWindowInstance)
    
    // 🗺️ THIS IS WHERE MARKERS GET PLOTTED ON THE MAP
    markers.forEach((markerData) => {
        const marker = new google.maps.Marker({
            position: markerData.position,  // lat, lng coordinates
            map: mapInstance,               // Google Maps instance
            title: markerData.title,        // Hover text
            icon: markerData.icon          // Marker color/icon
        })

        // Add click listener for info popup
        marker.addListener('click', () => {
            // Show info window when clicked
        })
    })
  }

  const getSafetyColor = (level: string): string => {
    switch (level.toLowerCase()) {
      case 'very_safe': return '#22c55e'
      case 'safe': return '#eab308'
      case 'moderate': return '#f97316'
      case 'high_risk': return '#ef4444'
      default: return '#6b7280'
    }
  }

  if (loading) {
    return (
      <div className="w-full h-[600px] bg-gray-900 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-gray-600 border-t-white mx-auto mb-4"></div>
          <p className="text-gray-400">Loading safety data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full h-[600px] bg-gray-900 border border-gray-800 rounded-lg p-8 text-center">
        <div className="text-red-400 mb-4">
          <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">Error Loading Safety Data</h3>
        <p className="text-gray-400 mb-4">{error}</p>
        <button 
          onClick={fetchSafetyData}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="w-full">
      <div className="mb-4 p-4 bg-gray-800 rounded-lg">
        <h2 className="text-xl font-bold text-white mb-2">Waterloo Parking Safety Map</h2>
        <p className="text-gray-300 text-sm">
          Showing {markers.length} parking locations with safety analysis
        </p>
        <div className="flex gap-4 mt-2 text-sm">
          <span className="flex items-center gap-1">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            Very Safe
          </span>
          <span className="flex items-center gap-1">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            Safe
          </span>
          <span className="flex items-center gap-1">
            <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
            Moderate
          </span>
          <span className="flex items-center gap-1">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            High Risk
          </span>
        </div>
      </div>
      
      <GoogleMap
        apiKey={apiKey}
        center={{ lat: 43.4723, lng: -80.5449 }}
        zoom={13}
        height="600px"
        onMapLoad={handleMapLoad}
        markers={[]} // We handle markers manually in handleMapLoad
      />
    </div>
  )
} 