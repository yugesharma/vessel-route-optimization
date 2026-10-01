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
  const [fuelTimeWeight, setFuelTimeWeight] = useState(0.5)
  const [startLocation, setStartLocation] = useState('')
  const [endLocation, setEndLocation] = useState('')
  const [basicRoutePoints, setBasicRoutePoints] = useState<[number, number][]>([])
  const [optimizedRoutePoints, setOptimizedRoutePoints] = useState<[number, number][]>([])
  const [dateTime, setDateTime] = useState('')
  const [routeDistance, setRouteDistance] = useState<number | null>(null)
  const [duration, setDuration] = useState<number | null>(null)
  const [optimizedRouteDistance, setOptimizedRouteDistance] = useState<number | null>(null)
  const [optimizedRouteTime, setOptimizedRouteTime] = useState<number | null>(null)
  const [optimizedRouteFuel, setOptimizedRouteFuel] = useState<number | null>(null)
  const [optimizedRouteAvgSpeed, setOptimizedRouteAvgSpeed] = useState<number | null>(null)
  const [waveOverlayUrl, setWaveOverlayUrl] = useState<string | null>(null)
  const [overlayBounds, setOverlayBounds] = useState<{
    north: number
    south: number
    east: number
    west: number
  } | null>(null)


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
      
      setBasicRoutePoints([])
      setOptimizedRoutePoints([])

        const response = await calculateRoute(startPoint, endPoint, dateTime, distanceWeight, windWeight, waveWeight, fuelTimeWeight)

        setWaveOverlayUrl(response.data.waveOverlayUrl)
        setOverlayBounds(response.data.overlayBounds)
        
        console.log(response.data)
        
        const points = response.data.basicRoute.geometry.coordinates.map(
          (point: [number, number]) => [point[1], point[0]] as [number, number])
          setBasicRoutePoints(points)
         
        const legs = response.data.optimizedRoute ?? []

        const optimizedDistance = legs.reduce((sum: number, leg: any) => { return sum + leg.distNm},0)
        const optimizedTime = legs.reduce((sum: number, leg: any) => { return sum + leg.timeH},0)
        const optimizedFuel = legs.reduce((sum: number, leg: any) => { return sum + leg.fuelKg},0)
        const optimizedAvgSpeed = optimizedDistance / optimizedTime
        
        
        setOptimizedRouteAvgSpeed(optimizedAvgSpeed)
        setOptimizedRouteDistance(optimizedDistance)
        setOptimizedRouteTime(optimizedTime)
        setOptimizedRouteFuel(optimizedFuel)
        
        console.log("Optimized average speed:", optimizedAvgSpeed)
        console.log("Optimized fuel:", optimizedFuel)
        console.log("Optimized distance:", optimizedDistance)
        console.log("Optimized time:", optimizedTime)

        const optimizedPoints = legs.map(
          (leg: any) => [leg.lat, leg.lon] as [number, number])
        
        setOptimizedRoutePoints(optimizedPoints)
        setRouteDistance(response.data.basicRoute.properties.length)
        setDuration(response.data.basicRoute.properties.duration_hours)
        }

  return (
    <div className="app-layout">
      <Sidebar startPoint={startPoint} startLocation={startLocation} setStartLocation={setStartLocation} endPoint={endPoint} endLocation={endLocation} setEndLocation={setEndLocation} setDateTime={setDateTime} dateTime={dateTime} distanceWeight={distanceWeight} setDistanceWeight={setDistanceWeight} windWeight={windWeight} setWindWeight={setWindWeight} waveWeight={waveWeight} setWaveWeight={setWaveWeight} handleStartLocationSearch={handleStartLocationChange} handleEndLocationSearch={handleEndLocationChange} generateRoute={generateRoute} routeDistance={routeDistance} duration={duration} fuelTimeWeight={fuelTimeWeight} setFuelTimeWeight={setFuelTimeWeight} />
      <MapView startPoint={startPoint} setStartPoint={setStartPoint} endPoint={endPoint} setEndPoint={setEndPoint} setStartLocation={setStartLocation} setEndLocation={setEndLocation} basicRoutePoints={basicRoutePoints} optimizedRoutePoints={optimizedRoutePoints} optimizedRouteDistance={optimizedRouteDistance} optimizedRouteTime={optimizedRouteTime} optimizedRouteFuel={optimizedRouteFuel} optimizedRouteAvgSpeed={optimizedRouteAvgSpeed} routeDistance={routeDistance} duration={duration} waveOverlayUrl={waveOverlayUrl} overlayBounds={overlayBounds} />
    </div>
  )
}


export default App
