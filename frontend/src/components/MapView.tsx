import { MapContainer, TileLayer, useMapEvents, CircleMarker, Polyline, useMap, ImageOverlay, Pane } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { useState, useEffect, useRef, memo } from 'react'
import WeatherSlider from './WeatherSlider'
import { Waves } from 'lucide-react'
import Legend from './Legend'
import AnimatedMapBoat from './animatedBoat'

type MapClickHandlerProps = {
  onMapClick: (latlng: [number, number]) => void
  onHover: (latlng: [number, number]) => void
}

function MapClickHandler({onMapClick, onHover}: MapClickHandlerProps) {
  useMapEvents({
    click: (e) => {
      const wrappedCoords=e.latlng.wrap()
      onMapClick([wrappedCoords.lat, wrappedCoords.lng])
    },
    mousemove: (e) => {
      const wrappedCoords=e.latlng.wrap()
      onHover([wrappedCoords.lat, wrappedCoords.lng])
    }
  })

  return null
}

type MapViewProps = {
  showResults: boolean
  startPoint: [number, number] | null
  endPoint: [number, number] | null
  setStartPoint: (point: [number, number] | null) => void
  setEndPoint: (point: [number, number] | null) => void
  setStartLocation: (value: string) => void
  setEndLocation: (value: string) => void
  basicRoutePoints: [number, number][]
  optimizedRoutePoints: [number, number][]
  optimizedRouteDistance: number | null
  optimizedRouteTime: number | null
  optimizedRouteFuel: number | null
  optimizedRouteAvgSpeed: number | null
  routeDistance: number | null
  duration: number | null
  overlayReady: boolean
  overlayDate: string | null
  overlayHours: number[] | null
  exploredBatches: [number, number][][]
  frontierNodes: [number, number][]
  currBestPath: [number, number][] | null
  generating: boolean
}

const exploredStyle={color:'yellow'}

const ExploredBatch=memo(({nodes}:{nodes:[number,number][]})=> (
  <>
    {nodes.map((node,i)=>(
      <CircleMarker key={i} center={node} radius={0.5} pathOptions={exploredStyle} interactive={false}/>
    ))}
  </>
))

function MapUpdater({
  startPoint,
  endPoint,
  routePoints,
}: {
  startPoint: [number, number] | null
  endPoint: [number, number] | null
  routePoints: [number, number][]
}) {
  const map = useMap()

  useEffect(() => {
    if (routePoints.length > 0) {
      map.fitBounds(routePoints)
    } else if (startPoint && endPoint) {
      map.fitBounds([startPoint, endPoint])
    } else if (startPoint) {
      map.setView(startPoint, 7)
    }
  }, [startPoint, endPoint, routePoints, map])

  return null
}

function MapView({showResults, startPoint, endPoint, setStartPoint, setEndPoint, 
  setStartLocation, setEndLocation, basicRoutePoints, optimizedRoutePoints,
  optimizedRouteDistance, optimizedRouteTime, optimizedRouteFuel, optimizedRouteAvgSpeed,
  routeDistance, overlayReady, overlayDate, overlayHours, exploredBatches, currBestPath, generating }: MapViewProps) {
  const [selectingStart, setSelectingStart] = useState(true)
  const [selectedRoute, setSelectedRoute] = useState<'basic' | 'optimized' | null>(null)
  const hoverRef = useRef<HTMLDivElement>(null)
  const [selectedOverlayHour, setSelectedOverlayHour] = useState<number>(0)
  const [showWaveOverlay, setShowWaveOverlay] = useState(true)

  const handleMapClick = (latlng: [number, number]) => {
    if (showResults || generating) return 
    
    if (selectingStart) {
      setStartPoint(latlng)
      setSelectingStart(false)
      setStartLocation(`${latlng[0].toFixed(4)}, ${latlng[1].toFixed(4)}`)
    } else {
      setEndPoint(latlng)
      setSelectingStart(true)
      setEndLocation(`${latlng[0].toFixed(4)}, ${latlng[1].toFixed(4)}`)
    }
  }
  console.log("Selected route:", selectedRoute)

  const handleHover = (latlng: [number, number]) => {
    if (hoverRef.current) {
      hoverRef.current.textContent = `${latlng[0].toFixed(4)}, ${latlng[1].toFixed(4)}`
    }
  }
  
  return( 
  <div className={`map-wrapper${generating ? '' : ' search-done'}`}>
    <MapContainer
    center={[38,-74]}
    zoom={5}
    className="map-container"
    preferCanvas={true}
>
  <TileLayer
    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  />

  <MapUpdater startPoint={startPoint} endPoint={endPoint} routePoints={basicRoutePoints} />
  
  <MapClickHandler onMapClick={handleMapClick} onHover={handleHover} />

  

  {exploredBatches && exploredBatches.length > 0 && (
    <Pane name='explored' style={{zIndex:410}}>
      {exploredBatches.map((batch,i)=> <ExploredBatch key={i} nodes={batch} />)}
    </Pane>
  )}

{currBestPath && currBestPath.length > 0 && (
  <Pane name='bestPath' style={{zIndex:450}}>
  <Polyline positions={currBestPath} pathOptions={{ color: 'green',weight: 3 }} />
  </Pane>
  )}

  <AnimatedMapBoat basicRoutePoints={basicRoutePoints} exploredBatches={exploredBatches} generating={generating} />
  {startPoint && <CircleMarker center={basicRoutePoints[0] ?? startPoint} radius={5} pathOptions={{ color: 'red' }} />}

  {endPoint && <CircleMarker center={basicRoutePoints.at(-1) ?? endPoint} radius={5} pathOptions={{ color: 'blue' }} />}

  {showWaveOverlay && overlayReady && overlayHours && [-360, 0, 360].map(shift => (
    <ImageOverlay
      key={shift}
      url={`/wave-overlays/${overlayDate}/${overlayHours[selectedOverlayHour]}.png`}
      bounds={[[-85.0511, -180.125 + shift], [85.0511, 179.875 + shift]]}
      opacity={0.5}
    />
  ))}

  {basicRoutePoints && basicRoutePoints.length > 0 && (
  <Polyline positions={basicRoutePoints} pathOptions={{ color: 'blue', weight: selectedRoute === "basic" ? 7 : 3 }} eventHandlers={{
    mouseover: () => {
      setSelectedRoute("basic")
    },
    mouseout: () => {
      setSelectedRoute(null)
    },
 }}/>
)}


  {/* {frontierNodes && frontierNodes.length > 0 && (
    frontierNodes.map((node) => (
      <CircleMarker key={node[0] + ',' + node[1]} center={node} radius={0.5} pathOptions={{ color: 'red' }} />
    ))
  )} */}


  {optimizedRoutePoints && optimizedRoutePoints.length > 0 && (
  <Polyline positions={optimizedRoutePoints} pathOptions={{ color: 'green',weight: selectedRoute === "optimized" ? 7 : 3 }} eventHandlers={{
    mouseover: () => {
      setSelectedRoute("optimized")
    },
    mouseout: () => {
      setSelectedRoute(null)
    }
  }}/>
)}

</MapContainer>

{selectedRoute && (
  <div className="route-info-panel">
  <strong>
    {selectedRoute === "basic" ? "Basic Route" : "Optimized Route"}
  </strong>

  {selectedRoute === "basic" && (
    <div>
      <div>
      Distance: {routeDistance?.toFixed(1)} nm
    </div>
    <div>
      {routeDistance !== null && optimizedRouteAvgSpeed != null && (
        <div>
          Time: {(routeDistance/optimizedRouteAvgSpeed).toFixed(1)} hours
          </div>
      )}
    </div>
  <div>
    Average Speed: {optimizedRouteAvgSpeed?.toFixed(1)} kn
  </div>
    </div>
  )}

  {selectedRoute === "optimized" && (
    <div>
      <div>
      Distance: {optimizedRouteDistance?.toFixed(1)} nm
    </div>
    <div>
      Time: {optimizedRouteTime?.toFixed(1)} hours
    </div>
    <div>
      Fuel: {optimizedRouteFuel?.toFixed(1)} kg
    </div>
    <div>
      Average Speed: {optimizedRouteAvgSpeed?.toFixed(1)} kn
    </div>
    </div>
  )}
</div>
)}

<div ref={hoverRef} className="hover-info-panel" />
<button
  className={`wave-toggle ${showWaveOverlay ? 'active' : ''}`}
  onClick={() => setShowWaveOverlay(!showWaveOverlay)}
  aria-label="Toggle wave overlay"
  aria-pressed={showWaveOverlay}
  title="Toggle wave overlay"
>
  <Waves size={20} strokeWidth={1.75} />
</button>
  <Legend visible={showWaveOverlay} />
  <WeatherSlider overlayReady={overlayReady} overlayDate={overlayDate} overlayHours={overlayHours} selectedOverlayHour={selectedOverlayHour} setSelectedOverlayHour={setSelectedOverlayHour}/>
</div>
);
}


export default MapView;