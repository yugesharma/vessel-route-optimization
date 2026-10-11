import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
})

export function calculateOptimizedRoute(startPoint: [number, number], endPoint: [number, number], dateTime: string, distanceWeight: number, windWeight: number, waveWeight: number, fuelTimeWeight: number) {
  return api.post('/optimizedRoute', { startPoint, endPoint, dateTime, distanceWeight, windWeight, waveWeight, fuelTimeWeight })
}

export function getBaseRoute(startPoint: [number, number], endPoint: [number, number]) {
  return api.get('/baseRoute', { params: { startPointLat: startPoint[0], startPointLon: startPoint[1], endPointLat: endPoint[0], endPointLon: endPoint[1] } })
}

export function getOverlayInfo() {
  return api.get('/overlays')
}