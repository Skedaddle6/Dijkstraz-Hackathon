from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import json
from database import SessionLocal, init_db, User, Incident, Alert
from pydantic import BaseModel

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Database
init_db()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class IncidentCreate(BaseModel):
    title: str
    description: str
    type: str
    lat: float
    lng: float
    is_anonymous: bool = False
    reporter_id: int

class AlertCreate(BaseModel):
    message: str
    type: str
    lat: float
    lng: float
    sender_id: int
