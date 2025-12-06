from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import json
from database import SessionLocal, init_db, User, Incident, Alert
from pydantic import BaseModel

app = FastAPI()

#static files mount gareko
app.mount("/static", StaticFiles(directory="static"), name="static")

#database initializing
init_db()

#For database, dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

class IoTNoiseAlert(BaseModel):
    device_id: str
    noise_level: float
    lat: float
    lng: float
    timestamp: float

class PetUpdate(BaseModel):
    pet_name: str
    owner_name: str
    breed: str
    lat: float
    lng: float
    is_safe: bool
    home_lat: float
    home_lng: float
    radius: float



#manager for websockett
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
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/incidents")
async def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    db_incident = Incident(**incident.dict())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    
    #telling everyone about incident
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

@app.post("/api/iot/noise")
async def report_noise(alert: IoTNoiseAlert, db: Session = Depends(get_db)):
    print(f"Received High Noise Alert from {alert.device_id}: {alert.noise_level:.2f} dB at ({alert.lat}, {alert.lng})")

    db_alert = Alert(
        message=f"High noise level detected: {alert.noise_level:.2f} dB",
        type="noise_warning",
        lat=alert.lat,
        lng=alert.lng,
        sender_id=1 
    )
    db.add(db_alert)
    db.commit()
    

    await manager.broadcast(json.dumps({
        "type": "noise_warning",
        "data": {
            "message": f"High noise ({alert.noise_level:.1f} dB) detected at {alert.lat}, {alert.lng}",
            "lat": alert.lat,
            "lng": alert.lng,
            "level": alert.noise_level
        }
    }))
    

    print(f"🔔 SIMULATION: Sending SMS to neighbors near ({alert.lat}, {alert.lng}): 'High noise detected in your area. Please keep it down.'")
    
    return {"status": "alert_processed", "action": "neighbors_notified"}

@app.get("/api/alerts")
async def get_alerts(db: Session = Depends(get_db)):

    return db.query(Alert).order_by(Alert.created_at.desc()).limit(50).all()

@app.post("/api/pet/update")
async def update_pet_location(update: PetUpdate, db: Session = Depends(get_db)):

    await manager.broadcast(json.dumps({
        "type": "pet_update",
        "data": update.dict()
    }))
    
    if not update.is_safe:
 
        message = f"{update.owner_name}'s dog {update.pet_name} of breed {update.breed} has gone missing, please help locate him."
        

        # For simulation
        db_alert = Alert(
            message=message,
            type="pet_missing",
            lat=update.lat,
            lng=update.lng,
            sender_id=1
        )
        db.add(db_alert)
        db.commit()
        
        await manager.broadcast(json.dumps({
            "type": "pet_missing",
            "data": {
                "message": message,
                "lat": update.lat,
                "lng": update.lng,
                "pet_name": update.pet_name
            }
        }))

    return {"status": "updated"}



import subprocess
import sys

@app.post("/api/simulate/sound")
async def simulate_sound():
    subprocess.Popen([sys.executable, "iot_simulation.py"])
    return {"status": "simulation_started", "type": "sound"}

@app.post("/api/simulate/pet")
async def simulate_pet():
    subprocess.Popen([sys.executable, "pet_simulation.py"])
    return {"status": "simulation_started", "type": "pet"}


