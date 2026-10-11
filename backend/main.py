# main.py

import asyncio
from environmentDataService import getWeatherData, DATE_STRING, FORECAST_HOURS
from RouteCalculation import calculateOptimizedRoute, getBaseRoute
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.weather=asyncio.create_task(asyncio.to_thread(getWeatherData))
    yield

app = FastAPI(lifespan=lifespan)

waveOverlayDir = os.path.join(os.path.dirname(__file__), "data", "waveOverlays", DATE_STRING)
os.makedirs(waveOverlayDir, exist_ok=True)   
app.mount("/wave-overlays", StaticFiles(directory=waveOverlayDir), name="wave-overlays")

load_dotenv()
geoapify_api_key = os.getenv("GEOAPIFY_API_KEY")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def geocode_location(location: str):
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {
        "text": location,
        "apiKey": geoapify_api_key
    }
    response = requests.get(url, params=params)
    data = response.json()

    lat = data['features'][0]['properties']['lat']
    lon = data['features'][0]['properties']['lon']

    return (lat, lon)


class RouteRequest(BaseModel):
    startPoint: tuple[float, float]
    endPoint: tuple[float, float]
    dateTime: str
    distanceWeight: float
    windWeight: float
    waveWeight: float
    fuelTimeWeight: float


@app.get("/geocode")
async def geocode(location: str):
    coordinates = geocode_location(location)
    return {"coordinates": coordinates}

def runRoute(request: RouteRequest, onProgress=None):
    startPoint = (request.startPoint[1], request.startPoint[0])
    endPoint = (request.endPoint[1], request.endPoint[0])
    baseRoute = getBaseRoute(startPoint, endPoint)
    optimizedRoute  = calculateOptimizedRoute(
        baseRoute,startPoint, endPoint, request.dateTime, distanceWeight=request.distanceWeight,
        fuelTimeWeight=request.fuelTimeWeight, onProgress=onProgress)
    return {"optimizedRoute": optimizedRoute}

@app.get("/baseRoute")
async def baseRoute(startPointLat: float, startPointLon: float, endPointLat: float, endPointLon: float):
    startPoint = (startPointLon, startPointLat)
    endPoint = (endPointLon, endPointLat)
    return {"baseRoute": getBaseRoute(startPoint, endPoint)}

@app.post("/optimizedRoute")
async def calculate_route(request: RouteRequest):
    return runRoute(request)

@app.websocket("/ws/route")
async def route_websocket(websocket: WebSocket):
    await websocket.accept()
    request = RouteRequest(**await websocket.receive_json())
    loop = asyncio.get_running_loop()

    # A* runs in a worker thread
    def onProgress(snapshot):
        asyncio.run_coroutine_threadsafe(websocket.send_json({"type": "progress", **snapshot}), loop).result()

    result = await asyncio.to_thread(runRoute, request, onProgress)
    await websocket.send_json({"type": "result", **result})
    await websocket.close()

@app.get("/overlays")
def overlays():
    done=os.path.join(waveOverlayDir, "done")
    return {"done": os.path.exists(done), "date": DATE_STRING, "hours": FORECAST_HOURS}