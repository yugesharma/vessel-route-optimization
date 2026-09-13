import { useState } from 'react'
import { calculateRoute } from '../api.ts'

type SidebarProps = {
  startPoint: [number, number] | null
  endPoint: [number, number] | null
  routePoints: [number, number][]
  setRoutePoints: (points: [number, number][]) => void
}

function Sidebar({startPoint, endPoint, setRoutePoints}: SidebarProps) {
  const [distanceWeight, setDistanceWeight] = useState(0.5)
  const [windWeight, setWindWeight] = useState(0.5)
  const [waveWeight, setWaveWeight] = useState(0.5)

  const handleCalculateRoute = async () => {
    if (!startPoint || !endPoint) return
    const response = await calculateRoute(startPoint, endPoint)
    setRoutePoints(response.data.route.geometry.coordinates.map((point: [number, number]) => [point[1], point[0]]))
  }

  return (
    <div className="sidebar">
      <h2>Route Planner</h2>
      <div className="form-group">
      <label htmlFor="start">Start Location:</label>
      <input type="text" id="startPoint" name="start" placeholder="Enter start location" value= {startPoint ? `${startPoint[0].toFixed(4)}, ${startPoint[1].toFixed(4)}` : ''} />
      </div>
      <div className="form-group">
      <label htmlFor="end">End Location:</label>
      <input type="text" id="endPoint" name="end" placeholder="Enter end location" value= {endPoint ? `${endPoint[0].toFixed(4)}, ${endPoint[1].toFixed(4)}` : ''} />
      </div>
      <div className="form-group">
        <label htmlFor="dateTime">Date/Time:</label>
        <input type="datetime-local" id="dateTime" name="dateTime" />
      </div>
      <h3>Route Preferences</h3>

    <div className="form-group">
      <div className="slider-header">
  <label htmlFor="distanceWeight">Distance Weight:</label>
  <span className="weight-value">{(distanceWeight * 100).toFixed(0)}%</span>
  </div>
        <input type="range" id="distanceWeight" name="distanceWeight" min="0" max="1" step="0.1" value={distanceWeight} onChange={(e) => setDistanceWeight(Number(e.target.value))} />
      </div>
  

<div className="form-group">
       <div className="slider-header">
  <label htmlFor="windWeight">Wind Weight:</label>
  <span className="weight-value">{(windWeight * 100).toFixed(0)}%</span>
  </div>
        <input type="range" id="windWeight" name="windWeight" min="0" max="1" step="0.1" value={windWeight} onChange={(e) => setWindWeight(Number(e.target.value))} />
      </div>

<div className="form-group">   
        <div className="slider-header">
  <label htmlFor="waveWeight">Wave Weight:</label>
  <span className="weight-value">{(waveWeight * 100).toFixed(0)}%</span>
  </div>
        <input type="range" id="waveWeight" name="waveWeight" min="0" max="1" step="0.1" value={waveWeight} onChange={(e) => setWaveWeight(Number(e.target.value))} />
      </div>
      
      <button onClick={handleCalculateRoute}>Calculate Route</button>
    </div>
  )
}

export default Sidebar