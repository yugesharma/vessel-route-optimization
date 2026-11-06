import L from 'leaflet'
import { useEffect, useState, useMemo } from 'react'
import { Marker, useMapEvents } from 'react-leaflet'


type AnimatedMapBoatProps = {
  basicRoutePoints: [number, number][]
  exploredBatches: [number, number][][]
  generating: boolean
}

function calculateBearing(
    start: [number, number],
    end: [number, number]
): number {
    const lat1 = start[0] * Math.PI /180
    const lat2 = end[0] * Math.PI /180
    const lonDiff = (end[1] - start[1]) * Math.PI /180
    const y = Math.sin(lonDiff) * Math.cos(lat2)
    const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(lonDiff)
    
    return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360
}

function AnimatedMapBoat({
  basicRoutePoints,
  exploredBatches,
  generating,
}: AnimatedMapBoatProps) {
  const [boatPosition, setBoatPosition] = useState<[number, number] | null>(null)
  const [progress, setProgress] = useState(0)
  const map = useMapEvents({
    zoomend: () => {
        setZoom(map.getZoom())
    },
  })

  const [zoom, setZoom] = useState(map.getZoom())

  const boatSize = Math.max(24, Math.min(80, 32 * Math.pow(1.3, zoom - 5)))

  const segmentIndex = Math.min(Math.floor(progress), Math.max(0, basicRoutePoints.length - 2))

  const bearing = basicRoutePoints.length >= 2 ? calculateBearing(basicRoutePoints[segmentIndex], basicRoutePoints[segmentIndex + 1]): 0

  const exploredProgress = useMemo(() => {
    if (basicRoutePoints.length < 2) return 0

    const exploredNodes = exploredBatches.flat()
    if (exploredNodes.length === 0) return 0

    let furthest = 0

    for (const node of exploredNodes) {
        for (let i = 0; i < basicRoutePoints.length; i++) {
            const point = basicRoutePoints[i]

            const latDiff = node[0] - point[0]
            const longDiff = (node[1]- point[1]) * Math.cos(point[0] * Math.PI / 180)

            const distance = Math.sqrt(latDiff ** 2 + longDiff ** 2)

            // count explored nodes near blue route
            if (distance < 0.15) {
                furthest = Math.max(furthest, i)
            }
        }
    }

    return furthest
}, [exploredBatches, basicRoutePoints])

  const boatIcon = L.divIcon({
    className: 'map-boat-icon',
    html: `
        <div class="map-boat" style="width:${boatSize}px; height:${boatSize * 1.5}px;">
        <svg
            viewBox="0 0 60 120"
            width="100%"
            height="100%"
            xmlns="http://www.w3.org/2000/svg"
            style="transform: rotate(${bearing}deg); transform-origin: 50% 50%;"
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
    iconAnchor: [boatSize / 2, boatSize * 0.75],
    })

  useEffect(() => {
  if (basicRoutePoints.length < 2) {
    setBoatPosition(null)
    setProgress(0)
    return
  }

  const interval = setInterval(() => {
    setProgress(previous => {
      const destination = basicRoutePoints.length - 1

      const target = generating
        ? exploredProgress
        : destination

      if (previous >= target) return previous

      const speed = generating ? 0.15 : Math.max(0.5, destination / 30)

      return Math.min(previous + speed, target)
    })
  }, 50)

  return () => clearInterval(interval)
}, [generating, exploredProgress, basicRoutePoints])


useEffect(() => {
  if (basicRoutePoints.length < 2) return

  const index = Math.min(
    Math.floor(progress),
    basicRoutePoints.length - 2
  )

  const fraction = progress - index

  const start = basicRoutePoints[index]
  const end = basicRoutePoints[index + 1]

  const lat = start[0] + (end[0] - start[0]) * fraction
  const lng = start[1] + (end[1] - start[1]) * fraction

  setBoatPosition([lat, lng])
}, [progress, basicRoutePoints, generating])

if (!boatPosition) {
    return null
}

return (
    <Marker
    position ={boatPosition}
    icon = {boatIcon}
    interactive = {false}
    zIndexOffset={1000}
    />
)
}

export default AnimatedMapBoat