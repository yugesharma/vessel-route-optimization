type SidebarProps = {
  startPoint: [number, number] | null
  endPoint: [number, number] | null
  setDistanceWeight: (value: number) => void
  setWindWeight: (value: number) => void
  setWaveWeight: (value: number) => void
  distanceWeight: number
  windWeight: number
  waveWeight: number
  startLocation: string
  endLocation: string
  setStartLocation: (value: string) => void
  setEndLocation: (value: string) => void
  handleStartLocationSearch: () => void
  handleEndLocationSearch: () => void
  generateRoute: () => void
  dateTime: string
  setDateTime: (value: string) => void
  routeDistance: number | null
  duration: number | null
}



function Sidebar({distanceWeight, setDistanceWeight, windWeight, setWindWeight, waveWeight, setWaveWeight, startLocation, endLocation, setStartLocation, setEndLocation, handleStartLocationSearch, handleEndLocationSearch, generateRoute, dateTime, setDateTime, routeDistance, duration}: SidebarProps) {
  const durationDays = duration !== null ? Math.floor(duration / 24) : 0
  const durationHours = duration !== null ? duration % 24 : 0
  return (
    <div className="sidebar">
      <h2>Route Planner</h2>
      <div className="form-group">
      <label htmlFor="start">Start Location:</label>
      <input type="text" id="start" name="start" placeholder="Enter start location" value={startLocation} onChange={(e) => setStartLocation(e.target.value)} onKeyDown={(e) => {if (e.key === 'Enter') { handleStartLocationSearch() }}} />
      </div>
      <div className="form-group">
      <label htmlFor="end">End Location:</label>
      <input type="text" id="end" name="end" placeholder="Enter end location" value={endLocation} onChange={(e) => setEndLocation(e.target.value)} onKeyDown={(e) => {if (e.key === 'Enter') { handleEndLocationSearch() }}} />
      </div>
      <div className="form-group">
        <label htmlFor="dateTime">Date/Time:</label>
        <input type="datetime-local" id="dateTime" name="dateTime" value={dateTime} onChange={(e) => setDateTime(e.target.value)} />
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
      
      <button onClick={generateRoute}>Calculate Route</button>
      {routeDistance !== null && (
        <div className="route-info">
          <h3>Route Information</h3>
          <p>Distance: {routeDistance.toFixed(2)} nautical miles</p>
          <p>Estimated Duration: {duration !== null ? `${durationDays} days, ${durationHours.toFixed(1)} hours`: 'N/A'}</p>
        </div>
  
      )}
    </div>
  )
}

export default Sidebar