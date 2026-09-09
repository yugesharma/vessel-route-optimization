from fastapi import FastAPI
from utils import getWaveData
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
    start: tuple[float, float]
    end: tuple[float, float]

@app.post("/route")
async def calculate_route(request: RouteRequest):
    # Here we would implement the logic to calculate the optimal route based on the start and ending points 
    # for now, return a placeholder response
    return {"route": [request.start, request.end], "message": "Route calculation not implemented yet"}
@app.get("/")
async def root():
    getWaveData()
    return {"message": "Wave data downloaded successfully"}