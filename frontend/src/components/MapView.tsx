import { MapContainer, TileLayer, useMapEvents, CircleMarker, Polyline, useMap, ImageOverlay } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { useState, useEffect } from 'react'

type MapClickHandlerProps = {
  onMapClick: (latlng: [number, number]) => void
}

function MapClickHandler({onMapClick}: MapClickHandlerProps) {
  useMapEvents({
    click: (e) => {
      onMapClick([e.latlng.lat, e.latlng.lng])
}
  })

  return null
}

type MapViewProps = {
  startPoint: [number, number] | null
  endPoint: [number, number] | null
  setStartPoint: (point: [number, number] | null) => void
  setEndPoint: (point: [number, number] | null) => void
  setStartLocation: (value: string) => void
  setEndLocation: (value: string) => void
  basicRoutePoints: [number, number][]
  optimizedRoutePoints: [number, number][]
  optimizedRouteDistance: number | null
  optimizedRouteTime: number | null
  optimizedRouteFuel: number | null
  optimizedRouteAvgSpeed: number | null
  routeDistance: number | null
  duration: number | null
  waveOverlayUrl: string | null
  overlayBounds: {
    north: number
    south: number
    east: number
    west: number
  } | null
}

function MapUpdater({
  startPoint,
  endPoint,
}: {
  startPoint: [number, number] | null
  endPoint: [number, number] | null
}) {
  const map = useMap()

  useEffect(() => {
    if (startPoint && endPoint) {
      map.fitBounds([startPoint, endPoint])
    } else if (startPoint) {
      map.setView(startPoint, 7)
    }
  }, [startPoint, endPoint, map])

  return null
}

function MapView({ startPoint, endPoint, setStartPoint, setEndPoint, setStartLocation, setEndLocation, basicRoutePoints, optimizedRoutePoints, optimizedRouteDistance, optimizedRouteTime, optimizedRouteFuel, optimizedRouteAvgSpeed, routeDistance, duration, waveOverlayUrl, overlayBounds }: MapViewProps) {
  const [selectingStart, setSelectingStart] = useState(true)
  const [selectedRoute, setSelectedRoute] = useState<'basic' | 'optimized' | null>(null)
  const handleMapClick = (latlng: [number, number]) => {
    if (selectingStart) {
      setStartPoint(latlng)
      setSelectingStart(false)
      setStartLocation(`${latlng[0].toFixed(4)}, ${latlng[1].toFixed(4)}`)
    } else {
      setEndPoint(latlng)
      setSelectingStart(true)
      setEndLocation(`${latlng[0].toFixed(4)}, ${latlng[1].toFixed(4)}`)
    }
  }
  console.log("Selected route:", selectedRoute)

  return( 
  <div className="map-wrapper">
    <MapContainer
    center={[38,-74]}
    zoom={5}
    className="map-container"
>
  <TileLayer
    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    noWrap={true}  
  />

  <MapUpdater startPoint={startPoint} endPoint={endPoint} />
  
  <MapClickHandler onMapClick={handleMapClick} />
  
  {startPoint && <CircleMarker center={startPoint} radius={5} pathOptions={{ color: 'red' }} />}
  
  {endPoint && <CircleMarker center={endPoint} radius={5} pathOptions={{ color: 'blue' }} />}

  {waveOverlayUrl && overlayBounds && (
  <ImageOverlay
    url={`http://127.0.0.1:8000${waveOverlayUrl}`}
    bounds={[
      [overlayBounds.south, overlayBounds.west],
      [overlayBounds.north, overlayBounds.east]
    ]}
    opacity={0.5}
  />
)}

  {basicRoutePoints && basicRoutePoints.length > 0 && (
  <Polyline positions={basicRoutePoints} pathOptions={{ color: 'blue', weight: selectedRoute === "basic" ? 7 : 3 }} eventHandlers={{
    mouseover: () => {
      setSelectedRoute("basic")
    },
    mouseout: () => {
      setSelectedRoute(null)
    },
 }}/>
)}

  {optimizedRoutePoints && optimizedRoutePoints.length > 0 && (
  <Polyline positions={optimizedRoutePoints} pathOptions={{ color: 'green',weight: selectedRoute === "optimized" ? 7 : 3 }} eventHandlers={{
    mouseover: () => {
      setSelectedRoute("optimized")
      console.log("Selected Route: Optimized")
    },
    mouseout: () => {
      setSelectedRoute(null)
    }
  }}/>
)}

</MapContainer>

{selectedRoute && (
  <div className="route-info-panel">
  <strong>
    {selectedRoute === "basic" ? "Basic Route" : "Optimized Route"}
  </strong>

  {selectedRoute === "basic" && (
    <div>
      <div>
      Distance: {routeDistance?.toFixed(1)} nm
    </div>
    <div>
      {routeDistance !== null && optimizedRouteAvgSpeed != null && (
        <div>
          Time: {(routeDistance/optimizedRouteAvgSpeed).toFixed(1)} hours
          </div>
      )}
    </div>
  <div>
    Average Speed: {optimizedRouteAvgSpeed?.toFixed(1)} kn
  </div>
    </div>
  )}

  {selectedRoute === "optimized" && (
    <div>
      <div>
      Distance: {optimizedRouteDistance?.toFixed(1)} nm
    </div>
    <div>
      Time: {optimizedRouteTime?.toFixed(1)} hours
    </div>
    <div>
      Fuel: {optimizedRouteFuel?.toFixed(1)} kg
    </div>
    <div>
      Average Speed: {optimizedRouteAvgSpeed?.toFixed(1)} kn
    </div>
    </div>
  )}
</div>
)}

</div>
)
}


export default MapView;