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


# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or process data if needed
            # await manager.broadcast(f"Message text was: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/incidents")
async def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    db_incident = Incident(**incident.dict())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    
    # Broadcast incident to all connected clients
    await manager.broadcast(json.dumps({
        "type": "incident",
        "data": {
            "title": incident.title,
            "description": incident.description,
            "lat": incident.lat,
            "lng": incident.lng,
            "type": incident.type
        }
    }))
    return db_incident


@app.get("/api/incidents")
async def get_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).all()

@app.post("/api/sos")
async def trigger_sos(alert: AlertCreate, db: Session = Depends(get_db)):
    db_alert = Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    # Broadcast SOS to all connected clients
    await manager.broadcast(json.dumps({
        "type": "sos",
        "data": {
            "message": alert.message,
            "lat": alert.lat,
            "lng": alert.lng,
            "sender_id": alert.sender_id
        }
    }))
    return db_alert
