import './App.css'
import MapView from './components/MapView'
import Sidebar from './components/Sidebar'
import { useState } from 'react'


function App() {
  const [startPoint, setStartPoint] = useState<[number, number] | null>(null)
  const [endPoint, setEndPoint] = useState<[number, number] | null>(null)
  const [routePoints, setRoutePoints] = useState<[number, number][]>([])

  return (
    <div className="app-layout">
      <Sidebar startPoint={startPoint} endPoint={endPoint} routePoints={routePoints} setRoutePoints={setRoutePoints} />
      <MapView startPoint={startPoint} setStartPoint={setStartPoint} endPoint={endPoint} setEndPoint={setEndPoint} routePoints={routePoints} setRoutePoints={setRoutePoints} />
    </div>
  )
}


export default App
