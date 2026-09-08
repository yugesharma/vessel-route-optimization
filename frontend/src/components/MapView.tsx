import { MapContainer, TileLayer, useMapEvents, CircleMarker, Polyline } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { useState } from 'react'

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

function MapView() {
  const [ startPoint, setStartPoint] = useState<[number, number] | null>(null)
  const [endPoint, setEndPoint] = useState<[number, number] | null>(null)
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

  {startPoint && endPoint && (
  <Polyline positions={[startPoint, endPoint]} />
)}
</MapContainer>

}


export default MapView;