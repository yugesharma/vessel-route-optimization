import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
})

export function calculateRoute(startPoint: [number, number], endPoint: [number, number]) {
  return api.post('/route', { startPoint, endPoint })
}
