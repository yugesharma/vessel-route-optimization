import { MapContainer, TileLayer, useMapEvents, CircleMarker, Polyline, useMap } from 'react-leaflet'
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
  routePoints: [number, number][]
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

function MapView({ startPoint, endPoint, setStartPoint, setEndPoint, setStartLocation, setEndLocation, routePoints }: MapViewProps) {
  const [selectingStart, setSelectingStart] = useState(true)
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
  
  return <MapContainer
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

  {routePoints && routePoints.length > 0 && (
  <Polyline positions={routePoints} />
)}
</MapContainer>

}


export default MapView;