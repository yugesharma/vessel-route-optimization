import './App.css'
import MapView from './components/MapView'
import Sidebar from './components/Sidebar'
import { useState } from 'react'


function App() {
  const [startPoint, setStartPoint] = useState<[number, number] | null>(null)
  const [endPoint, setEndPoint] = useState<[number, number] | null>(null)

  return (
    <div className="app-layout">
      <Sidebar startPoint={startPoint} endPoint={endPoint} />
      <MapView startPoint={startPoint} setStartPoint={setStartPoint} endPoint={endPoint} setEndPoint={setEndPoint} />
    </div>
  )
}


export default App
