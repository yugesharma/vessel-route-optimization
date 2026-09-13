from fastapi import FastAPI
from utils import getWaveData
from RouteCalculation import calculateRoute
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RouteRequest(BaseModel):
    startPoint: tuple[float, float]
    endPoint: tuple[float, float]

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