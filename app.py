import asyncio
import socketio
import uvicorn
import logging
import RPi.GPIO as GPIO




from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from repositories.DataRepository import DataRepository
from models.models import DTOLampStatus, LampStatus

# ----------------------------------------------------
# Logging
# ----------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# ----------------------------------------------------
# Pins Constants
# ----------------------------------------------------
LED_PIN = 17      
BUTTON_PIN = 20    

# ----------------------------------------------------
# Global state (optioneel)
# ----------------------------------------------------
led_state = False

# ----------------------------------------------------
# App setup
# ----------------------------------------------------
@asynccontextmanager
async def lifespan_manager(app: FastAPI):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    logger.info("GPIO initialised")

    # Start background
    loop = asyncio.get_running_loop()
    loop.create_task(tweede_thread())

    yield  # Geef controle aan FastAPI/Socket.IO

    # GPIO cleanup
    GPIO.cleanup()
    logger.info("GPIO cleaned up – bye!")

app = FastAPI(lifespan=lifespan_manager)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi', logger=True)
sio_app = socketio.ASGIApp(sio, app)

ENDPOINT = "/api/v1"

# ----------------------------------------------------
# Background Tasks
# ----------------------------------------------------
async def allesuit():
    print("[allesuit] Gestart. Alles uit!")
    DataRepository.update_status_alle_lampen(0)

    # Zet fysieke lamp 1 uit
    GPIO.output(LED_PIN, GPIO.LOW)

    # Emit naar clients
    await sio.emit('B2F_alles_uit', {'status': 'connected'})
    new_statuses = DataRepository.read_status_lampen()
    await sio.emit('B2F_status_lampen', {'lampen': new_statuses})

    return {"message": "Alles uit!"}

async def tweede_thread():
    print("[alles_uit] Thread actief.")
    while True:
        await allesuit()
        await asyncio.sleep(10)

# ----------------------------------------------------
# FastAPI Endpoints
# ----------------------------------------------------
@app.get("/")
async def root():
    return "Server werkt, maar hier geen API endpoint gevonden."

@app.get("/routes")
async def get_routes():
    return {"available_routes": [{"path": route.path, "name": route.name, "methode": getattr(route, "methods", None)} for route in app.routes]}

@app.patch(ENDPOINT + "/lampen/{lamp_id}/status/", response_model=LampStatus, summary="Update lamp status")
async def update_lamp_status(lamp_id: int, status: DTOLampStatus):
    print(f"[RESTAPI] => Lamp {lamp_id} naar {status.nieuwe_status}")
    DataRepository.update_status_lamp(lamp_id, status.nieuwe_status)

    # GPIO aansturen indien lamp_id == 1
    if lamp_id == 1:
        GPIO.output(LED_PIN, GPIO.HIGH if status.nieuwe_status else GPIO.LOW)
        logger.info(f"LED op GPIO {LED_PIN} {'aan' if status.nieuwe_status else 'uit'} gezet")

    lamp_data = DataRepository.read_status_lamp_by_id(lamp_id)
    await sio.emit('B2F_verandering_lamp', {'lamp': lamp_data})
    return LampStatus(lamp=lamp_id, status=lamp_data['status'])

# ----------------------------------------------------
# Socket.IO Handlers
# ----------------------------------------------------
@sio.event
async def connect(sid, environ):
    print(f"[Socket.IO] Client geconnecteerd: {sid}")
    lampenstatus = DataRepository.read_status_lampen()
    await sio.emit('B2F_status_lampen', {'lampen': lampenstatus}, to=sid)

# ----------------------------------------------------
# Run the app
# ----------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("app:sio_app", host="0.0.0.0", port=8000, log_level="info", reload=True, reload_dirs=["backend"])
