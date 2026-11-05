import L from 'leaflet'
import { useEffect, useState } from 'react'
import { Marker, useMapEvents } from 'react-leaflet'

type AnimatedMapBoatProps = {
  basicRoutePoints: [number, number][]
  exploredBatches: [number, number][][]
  generating: boolean
}

function AnimatedMapBoat({
  basicRoutePoints,
  exploredBatches,
  generating,
}: AnimatedMapBoatProps) {
  const [boatPosition, setBoatPosition] = useState<[number, number] | null>(null)
  const map = useMapEvents({
    zoomend: () => {
        setZoom(map.getZoom())
    },
  })

  const [zoom, setZoom] = useState(map.getZoom())

  const boatSize = Math.max(24, Math.min(80, 32 * Math.pow(1.3, zoom - 5)))

  const boatIcon = L.divIcon({
    className: 'map-boat-icon',
    html: `
        <div class="map-boat" style="width:${boatSize}px; height:${boatSize * 1.5}px;">
        <svg
            viewBox="0 0 60 120"
            width="100%"
            height="100%"
            xmlns="http://www.w3.org/2000/svg"
        >
            <!-- Ship hull -->
            <path
            d="M 30 4
                Q 48 5 52 25
                L 52 105
                Q 52 116 42 116
                L 18 116
                Q 8 116 8 105
                L 8 25
                Q 12 5 30 4 Z"
            fill="#334155"
            stroke="#0f172a"
            stroke-width="3"
            />

            <!-- Deck -->
            <rect x="14" y="30" width="32" height="65" rx="3" fill="#b45309"/>

            <!-- Cargo tanks -->
            <g fill="#cbd5e1" stroke="#64748b" stroke-width="1.5">
            <rect x="18" y="35" width="24" height="13" rx="3"/>
            <rect x="18" y="53" width="24" height="13" rx="3"/>
            <rect x="18" y="71" width="24" height="13" rx="3"/>
            </g>

            <!-- Bridge -->
            <rect x="14" y="96" width="32" height="13" rx="2" fill="#f8fafc"/>
            <rect x="19" y="98" width="22" height="4" fill="#38bdf8"/>
        </svg>
        </div>
    `,
    iconSize: [boatSize, boatSize * 1.5],
    iconAnchor: [boatSize / 2, boatSize / 0.75],
    })

  useEffect(() => {
    if (!generating || basicRoutePoints.length === 0) {
      setBoatPosition(null)
      return
    }

    setBoatPosition(basicRoutePoints[0])
  }, [generating, basicRoutePoints])

  if (!generating || !boatPosition) {
    return null
  }

  return (
    <Marker
      position={boatPosition}
      icon={boatIcon}
      interactive={false}
    />
  )
}

export default AnimatedMapBoat