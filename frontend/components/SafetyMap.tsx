"use client"

import { useEffect, useState, useRef } from 'react'

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
  const [map, setMap] = useState<google.maps.Map | null>(null)
  const mapRef = useRef<HTMLDivElement>(null)
  
  // 🚩 FLAG to ensure map initializes exactly once
  const mapInitializedRef = useRef(false)

  useEffect(() => {
    fetchSafetyData()
  }, [])

  // Initialize map when we have both API key and markers
  useEffect(() => {
    if (apiKey && markers.length > 0 && !mapInitializedRef.current) {
      initMap()
    }
  }, [apiKey, markers])

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
      
      // Extract markers and explicitly type cast to SafetyMarker[] interface
      const safetyMarker: SafetyMarker[] = data.markers as SafetyMarker[] || []
      console.log(`✅ Loaded ${safetyMarker.length} safety markers`)
      
      setMarkers(safetyMarker)
      setLoading(false)
      
    } catch (err) {
      console.error('❌ Error fetching safety data:', err)
      setError(err instanceof Error ? err.message : 'Failed to load safety data')
      setLoading(false)
    }
  }

  const initMap = async (): Promise<void> => {
    // 🚩 CHECK FLAG - only run once
    if (mapInitializedRef.current) {
      console.log('⚠️ Map already initialized, skipping...')
      return
    }

    if (!mapRef.current) {
      console.error('❌ Map container not found')
      return
    }

    try {
      console.log('🗺️ Initializing Google Maps...')
      mapInitializedRef.current = true

      // Load Google Maps script dynamically
      if (!window.google) {
        await loadGoogleMapsScript()
      }

      // Request needed libraries
      //@ts-ignore
      const { Map } = await google.maps.importLibrary("maps") as google.maps.MapsLibrary
      const { AdvancedMarkerElement } = await google.maps.importLibrary("marker") as google.maps.MarkerLibrary

      // Create the map, centered on Waterloo
      const mapInstance = new Map(mapRef.current, {
        zoom: 13,
        center: { lat: 43.4723, lng: -80.5449 }, // Waterloo, ON
        mapId: 'WATERLOO_PARKING_MAP', // You'll need to create this in Google Cloud Console
      })

      setMap(mapInstance)
      console.log('✅ Map initialized successfully')

      // Add safety markers
      console.log(`📍 Adding ${markers.length} safety markers...`)
      
      for (let i = 0; i < markers.length; i++) {
        const markerData = markers[i]
        
        console.log(`📍 Adding marker ${i + 1}: ${markerData.location} at (${markerData.position.lat}, ${markerData.position.lng})`)
        
        // Create custom marker element with color based on safety
        const markerElement = createSafetyMarkerElement(markerData)
        
        // Create advanced marker
        const advancedMarker = new AdvancedMarkerElement({
          map: mapInstance,
          position: markerData.position,
          title: markerData.title,
          content: markerElement
        })

        // Add click listener for info window
        advancedMarker.addListener('click', () => {
          showInfoWindow(mapInstance, markerData, advancedMarker.position!)
        })
      }

      console.log('✅ All markers added successfully')

    } catch (error) {
      console.error('❌ Error initializing map:', error)
      setError('Failed to initialize map')
      mapInitializedRef.current = false // Reset flag on error
    }
  }

  const loadGoogleMapsScript = (): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (window.google) {
        resolve()
        return
      }

      const script = document.createElement('script')
      script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=marker`
      script.async = true
      script.defer = true
      
      script.onload = () => resolve()
      script.onerror = () => reject(new Error('Failed to load Google Maps script'))
      
      document.head.appendChild(script)
    })
  }

  const createSafetyMarkerElement = (markerData: SafetyMarker): HTMLElement => {
    const element = document.createElement('div')
    element.className = 'safety-marker'
    
    // Get color based on safety level
    const color = getSafetyColor(markerData.safety_level)
    
    element.innerHTML = `
      <div style="
        width: 20px;
        height: 20px;
        background-color: ${color};
        border: 2px solid white;
        border-radius: 50%;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
        color: white;
      ">
        🅿️
      </div>
    `
    
    return element
  }

  const showInfoWindow = (mapInstance: google.maps.Map, markerData: SafetyMarker, position: google.maps.LatLng | google.maps.LatLngLiteral) => {
    const infoWindow = new google.maps.InfoWindow({
      content: `
        <div style="max-width: 300px; font-family: Arial, sans-serif;">
          <h3 style="margin: 0 0 10px 0; color: #333;">${markerData.location}</h3>
          <div style="margin-bottom: 10px;">
            <strong>Safety Level:</strong> 
            <span style="color: ${getSafetyColor(markerData.safety_level)}; font-weight: bold;">
              ${markerData.safety_level.toUpperCase()}
            </span>
            (${markerData.safety_score.toFixed(2)})
          </div>
          <div style="margin-bottom: 10px;">
            <strong>Infractions:</strong> ${markerData.infraction_count}
          </div>
          ${markerData.details.has_street_parking ? 
            '<div style="margin-bottom: 5px;">🅿️ Street parking available</div>' : ''
          }
          ${markerData.details.nearby_lots > 0 ? 
            `<div style="margin-bottom: 5px;">🏢 ${markerData.details.nearby_lots} nearby lot(s)</div>` : ''
          }
          <div style="margin-top: 10px;">
            <strong>Key Points:</strong>
            <ul style="margin: 5px 0; padding-left: 20px;">
              ${markerData.details.reasoning.slice(0, 3).map(reason => 
                `<li style="margin: 2px 0; font-size: 12px;">${reason}</li>`
              ).join('')}
            </ul>
          </div>
        </div>
      `,
      position: position
    })
    
    infoWindow.open(mapInstance)
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
          onClick={() => {
            mapInitializedRef.current = false
            fetchSafetyData()
          }}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="w-full">
      <div className="mb-6 p-6 bg-gray-900/50 border border-gray-800 rounded-xl backdrop-blur-sm">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-white via-gray-300 to-gray-500 bg-clip-text text-transparent mb-3">
          Waterloo Parking Safety Map
        </h2>
        <p className="text-gray-400 text-base mb-4">
          Showing {markers.length} parking locations with safety analysis
        </p>
        <div className="flex flex-wrap gap-6 text-sm">
          <span className="flex items-center gap-2 text-gray-300">
            <div className="w-4 h-4 bg-green-500 rounded-full border-2 border-white shadow-lg"></div>
            <span className="font-medium">Very Safe</span>
          </span>
          <span className="flex items-center gap-2 text-gray-300">
            <div className="w-4 h-4 bg-yellow-500 rounded-full border-2 border-white shadow-lg"></div>
            <span className="font-medium">Safe</span>
          </span>
          <span className="flex items-center gap-2 text-gray-300">
            <div className="w-4 h-4 bg-orange-500 rounded-full border-2 border-white shadow-lg"></div>
            <span className="font-medium">Moderate</span>
          </span>
          <span className="flex items-center gap-2 text-gray-300">
            <div className="w-4 h-4 bg-red-500 rounded-full border-2 border-white shadow-lg"></div>
            <span className="font-medium">High Risk</span>
          </span>
        </div>
      </div>
      
      {/* Map container */}
      <div 
        ref={mapRef}
        className="w-full h-[600px] rounded-xl overflow-hidden border border-gray-800"
        id="map"
      />
    </div>
  )
} 