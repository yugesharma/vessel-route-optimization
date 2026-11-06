type SidebarProps = {
  startPoint: [number, number] | null
  endPoint: [number, number] | null
  maxWaveHeight: number
  setMaxWaveHeight: (value: number) => void
  fuelTimeWeight: number
  setFuelTimeWeight: (value: number) => void
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
  generating: boolean
}



function Sidebar({maxWaveHeight, setMaxWaveHeight, fuelTimeWeight, setFuelTimeWeight, startLocation, endLocation, setStartLocation, setEndLocation, handleStartLocationSearch, handleEndLocationSearch, generateRoute, dateTime, setDateTime, generating}: SidebarProps) {

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
        <label htmlFor="dateTime">Date/Time(UTC):</label>
        <input type="datetime-local" id="dateTime" name="dateTime" value={dateTime} onChange={(e) => setDateTime(e.target.value)} />
      </div>

      <h3>Route Preferences</h3>

<div className="form-group">
    <label htmlFor="fuelTimeWeight">Fuel vs. Time:</label>

        <div className="fuel-time-labels">
        <span> Save Fuel</span>
        <span> Save Time</span>
        </div>
        <input type="range" id="fuelTimeWeight" name="fuelTimeWeight" min="0" max="1" step="0.1" value={fuelTimeWeight} onChange={(e) => setFuelTimeWeight(Number(e.target.value))} />
        </div>

<div className="form-group">   
        <div className="slider-header">
  <label htmlFor="maxWaveHeight">Maximum Wave Height:</label>
  <span className="weight-value">{maxWaveHeight.toFixed(1)} m</span>
  </div>
        <input type="range" id="maxWaveHeight" name="maxWaveHeight" min="0" max="8.0" step="0.5" value={maxWaveHeight} onChange={(e) => setMaxWaveHeight(Number(e.target.value))} />
      </div>
       <div className="results-actions">
      <button onClick={generateRoute} disabled={generating}>{generating ? 'Calculating...' : 'Calculate Route'}</button>
    </div>
    </div>
  )
}

export default Sidebar