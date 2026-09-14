from fastapi import FastAPI
from utils import getWaveData
from RouteCalculation import calculateRoute
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests

app = FastAPI()

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

    
@app.get("/geocode")
async def geocode(location: str):
    coordinates = geocode_location(location)
    return {"coordinates": coordinates}

@app.post("/route")
async def calculate_route(request: RouteRequest):
    # Here we would implement the logic to calculate the optimal route based on the start and ending points 
    # for now, return a placeholder response
    startPoint = (request.startPoint[1], request.startPoint[0])
    endPoint = (request.endPoint[1], request.endPoint[0])
    route = calculateRoute(startPoint, endPoint)
    return {"route": route.baseRoute, "message": "Route calculation not implemented yet"}

@app.get("/")
async def root():
    getWaveData()
    return {"message": "Wave data downloaded successfully"}