
type ResultsSidebarProps = {
  startPoint: [number, number] | null
  endPoint: [number, number] | null
  startLocation: string
  endLocation: string
  dateTime: string
  optimizedRouteDistance: number | null
  optimizedRouteTime: number | null
  optimizedRouteFuel: number | null
  optimizedRouteAvgSpeed: number | null
  fuelTimeWeight: number
  setFuelTimeWeight: (value: number) => void
  waveWeight: number
  setWaveWeight: (value: number) => void
  generating: boolean
  generateRoute: () => void
  onBack: () => void
}

function ResultsSidebar({startPoint, endPoint, startLocation, endLocation, dateTime, optimizedRouteDistance, optimizedRouteTime, optimizedRouteFuel, optimizedRouteAvgSpeed, fuelTimeWeight, setFuelTimeWeight, waveWeight, setWaveWeight, generating, generateRoute, onBack}: ResultsSidebarProps) {
    const departureDate = new Date(dateTime)
    const arrivalDate = optimizedRouteTime !== null ? new Date(departureDate.getTime() + optimizedRouteTime * 3.6e6) : null

    return (
    <div className="sidebar results-sidebar">
      <h2>Route Results</h2>
      <div className="route-location">
        <h3>Departure</h3>
        <p>{startPoint?.join(', ')}</p>
        <p>{departureDate.toLocaleString('en-US', {weekday: "long", month: "long", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit", hour12: true})}</p>
        </div>
        <div className="route-location">
        <h3>Arrival</h3>
        <p>{endPoint?.join(', ')}</p>
        <p>{arrivalDate ? arrivalDate.toLocaleString('en-US', {weekday: "long", month: "long", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit", hour12: true}) : 'N/A'}</p>
        </div>

        <div className="route-details">
        <h3>Optimized Route Details</h3>
        <div className="route-details-row">
            <span>Total distance</span>
            <span>
                {optimizedRouteDistance != null
                ? optimizedRouteDistance.toFixed(2)
                : 'N/A'} NM
            </span>
            </div>
        <div className="route-details-row">
            <span>Duration</span>
            <span>{optimizedRouteTime != null ? (optimizedRouteTime).toFixed(2) : 'N/A'} hours</span>
        </div>
        <div className="route-details-row">
            <span>ETA</span>
            <span>{arrivalDate ? arrivalDate.toLocaleString('en-US', {weekday: "long", month: "long", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit", hour12: true}) : 'N/A'}</span>
        </div>
        <div className="route-details-row">
            <span>Total fuel consumption</span>
            <span>{optimizedRouteFuel != null ? (optimizedRouteFuel).toFixed(2) : 'N/A'} kg</span>
        </div>
        <div className="route-details-row">
            <span>Average speed</span>
            <span>{optimizedRouteAvgSpeed != null ? (optimizedRouteAvgSpeed).toFixed(2) : 'N/A'} kn</span>
        </div>
        </div>

        <div className="optimization-controls">
            <h3>Optimization Controls</h3>
        <div className="form-group">
            <div className="fuel-time-labels">
                <span> Save Fuel</span>
                <span> Save Time</span>
            </div>
        
            <input type="range" id="fuelTimeWeight" name="fuelTimeWeight" min="0" max="1" step="0.1" value={fuelTimeWeight} onChange={(e) => setFuelTimeWeight(Number(e.target.value))} />
        </div>
        
        
        <div className="form-group">   
            <div className="slider-header">
                <label htmlFor="waveWeight">Wave Height:</label>
                <span className="weight-value">{(waveWeight * 100).toFixed(0)}%</span>
            </div>
        
            <input type="range" id="waveWeight" name="waveWeight" min="0" max="1" step="0.1" value={waveWeight} onChange={(e) => setWaveWeight(Number(e.target.value))} />
        </div>
        </div>

     <div className="results-actions">
        <button onClick={generateRoute} disabled={generating}>
            {generating ? 'Recalculating...' : 'Recalculate Route'}
        </button>
        <button onClick={onBack} disabled={generating}>
            Back
        </button>
    </div>
    </div>
  )

}
export default ResultsSidebar