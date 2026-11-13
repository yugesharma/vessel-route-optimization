import { useState } from 'react'
import {DownloadRoute} from './DownloadRoute'

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
  maxWaveHeight: number
  setMaxWaveHeight: (value: number) => void
  basicRoute: [number, number][]
  optimizedRoute:[number, number][]
  generating: boolean
  generateRoute: () => void
  onBack: () => void
}

function ResultsSidebar({startPoint, endPoint, startLocation, endLocation, dateTime, optimizedRouteDistance, optimizedRouteTime, optimizedRouteFuel, optimizedRouteAvgSpeed, fuelTimeWeight, setFuelTimeWeight, maxWaveHeight, setMaxWaveHeight, basicRoute, optimizedRoute, generating, generateRoute, onBack}: ResultsSidebarProps) {
    const departureDate = new Date(dateTime)
    const arrivalDate = optimizedRouteTime !== null ? new Date(departureDate.getTime() + optimizedRouteTime * 3.6e6) : null
    const [downloadMenuOpen,setDownloadMenuOpen]=useState(false)

    function downloadRoute(e:string):void {
        let res=''
        if (e=='basic') res=DownloadRoute({routePoints:basicRoute,routeType:e})
        if (e=='optimized') res=DownloadRoute({routePoints:optimizedRoute,routeType:e})
        
        if (res=='done') setDownloadMenuOpen(!downloadMenuOpen) 
    }

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
            <p>{arrivalDate ? arrivalDate.toLocaleString('en-US', {weekday: "long", month: "long", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit", hour12: true}) :  generating ? 'Calculating ETA...' : 'N/A'}</p>
        </div>
        {generating ?(
            <div className="route-details calculating-state">
                <div className="boat-scene">
                    <svg viewBox="0 0 280 110" className="boat-svg" role="img" aria-label="Boat gently rocking on waves">
                        <g className="rocking-boat">
                            <path d="M 105 56 L 175 56 L 163 77 L 117 77 Z" fill="#3b82f6" />
                            <rect x="125" y="39" width="30" height="17" fill="#f8fafc" />
                            <rect x="131" y="44" width="18" height="8" rx="2" fill="#93c5fd" />
                        </g>
                        <path
                            className="boat-wave wave-one"
                            d="M 20 78 Q 50 65 80 78 T 140 78 T 200 78 T 260 78"
                            fill="none"
                            stroke="#60a5fa"
                            strokeWidth="3"
                            strokeLinecap="round"
                            />

                        <path
                            className="boat-wave wave-two"
                            d="M 20 93 Q 50 80 80 93 T 140 93 T 200 93 T 260 93"
                            fill="none"
                            stroke="#60a5fa"
                            strokeWidth="2"
                            strokeLinecap="round"
                            opacity="0.5"
                            />
                    </svg>
                    </div>
            <h3>Optimizing Your Route...</h3>
            <p>Analyzing weather conditions, vessel performance, and possible routes...</p>
            </div>
    ) : (
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
        )}

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
                    <label htmlFor="maxWaveHeight">Maximum Wave Height:</label>
                    <span className="weight-value">{maxWaveHeight.toFixed(1)} m</span>
                </div>
                <input type="range" id="maxWaveHeight" name="maxWaveHeight" min="0" max="8.0" step="0.5" value={maxWaveHeight} onChange={(e) => setMaxWaveHeight(Number(e.target.value))} />
                </div>
            </div>

        <div className="results-actions">
            <div className='route-buttons'>
                <button onClick={generateRoute} disabled={generating}>
                    {generating ? 'Recalculating...' : 'Recalculate Route'}
                </button>
                <button onClick={onBack} disabled={generating}>
                    Back
                </button>
            </div>
            <div className='download-menu'>
                <button onClick={()=>setDownloadMenuOpen(!downloadMenuOpen)} disabled={generating}>
                    Download Route
                </button>
                {downloadMenuOpen && (
                    <div className="download-options">
                        <button onClick={() => downloadRoute('optimized')}>Optimized Route</button>
                        <button onClick={() => downloadRoute('basic')}>Basic Route</button>
                    </div>
                )}
            </div>
        </div>
    </div>
  )

}
export default ResultsSidebar