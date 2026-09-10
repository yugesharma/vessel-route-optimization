import { MapContainer, TileLayer, useMapEvents, CircleMarker, Polyline } from 'react-leaflet'
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
}

function MapView({ startPoint, endPoint, setStartPoint, setEndPoint }: MapViewProps) {
  const [selectingStart, setSelectingStart] = useState(true)
  const handleMapClick = (latlng: [number, number]) => {
    if (selectingStart) {
      setStartPoint(latlng)
      setSelectingStart(false)
    } else {
      setEndPoint(latlng)
      setSelectingStart(true)
    }
  }
  const [routePoints, setRoutePoints] = useState<[number, number][]>([])
  const generateRoute = async () => {
    if (startPoint && endPoint) {
      setRoutePoints([])
      const response = await fetch('http://127.0.0.1:8000/route', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ start: startPoint, end: endPoint })
      });
      const result = await response.json();
      setRoutePoints(result.route);
    }
  }
  useEffect(() => {
    if (startPoint && endPoint) {
      generateRoute();
    }}, [startPoint, endPoint]);

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
  <MapClickHandler onMapClick={handleMapClick} />
  
  {startPoint && <CircleMarker center={startPoint} radius={5} pathOptions={{ color: 'red' }} />}
  
  {endPoint && <CircleMarker center={endPoint} radius={5} pathOptions={{ color: 'blue' }} />}

  {routePoints.length > 0 && (
  <Polyline positions={routePoints} />
)}
</MapContainer>

}


export default MapView;