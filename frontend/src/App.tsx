import './App.css'
import MapView from './components/MapView'
import Sidebar from './components/Sidebar'
import { useState } from 'react'
import { calculateRoute } from './api'


function App() {
  const [startPoint, setStartPoint] = useState<[number, number] | null>(null)
  const [endPoint, setEndPoint] = useState<[number, number] | null>(null)
  const [distanceWeight, setDistanceWeight] = useState(0.5)
  const [windWeight, setWindWeight] = useState(0.5)
  const [waveWeight, setWaveWeight] = useState(0.5)
  const [startLocation, setStartLocation] = useState('')
  const [endLocation, setEndLocation] = useState('')
  const [routePoints, setRoutePoints] = useState<[number, number][]>([])

  const handleStartLocationChange = async () => {
    const response = await fetch(
  `http://127.0.0.1:8000/geocode?location=${encodeURIComponent(startLocation)}`
  )
    const data = await response.json()
    setStartPoint(data.coordinates)
  }

  const handleEndLocationChange = async () => {
    const response = await fetch(
  `http://127.0.0.1:8000/geocode?location=${encodeURIComponent(endLocation)}`
  )
    const data = await response.json()
    setEndPoint(data.coordinates)
  }

  const generateRoute = async () => {
      if (!startPoint || !endPoint) return
      
      setRoutePoints([])

        const response = await calculateRoute(startPoint, endPoint)
        const points = response.data.route.geometry.coordinates.map(
          (point: [number, number]) => [point[1], point[0]] as [number, number])
        
        setRoutePoints(points)
      }

  return (
    <div className="app-layout">
      <Sidebar startPoint={startPoint} startLocation={startLocation} setStartLocation={setStartLocation} endPoint={endPoint} endLocation={endLocation} setEndLocation={setEndLocation} distanceWeight={distanceWeight} setDistanceWeight={setDistanceWeight} windWeight={windWeight} setWindWeight={setWindWeight} waveWeight={waveWeight} setWaveWeight={setWaveWeight} handleStartLocationSearch={handleStartLocationChange} handleEndLocationSearch={handleEndLocationChange} generateRoute={generateRoute}/>
      <MapView startPoint={startPoint} setStartPoint={setStartPoint} endPoint={endPoint} setEndPoint={setEndPoint} setStartLocation={setStartLocation} setEndLocation={setEndLocation} routePoints={routePoints} />
    </div>
  )
}


export default App
