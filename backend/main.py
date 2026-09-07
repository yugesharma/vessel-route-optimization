from fastapi import FastAPI
from utils import getWaveData

app = FastAPI()


@app.get("/")
async def root():
    getWaveData()
    return {"message": "Wave data downloaded successfully"}