from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


# Gebruiker tabel
class Gebruiker(BaseModel):
    GebruikerID: int
    Email: str
    Naam: str  # FIXED: was int, moet str zijn


# Device tabel  
class Device(BaseModel):
    DeviceID: int  # FIXED: was str, moet int zijn (AUTO_INCREMENT)
    Beschrijving: str  
    Actief_Sinds: datetime
    Is_Actief: bool  
    GebruikerID: int  


# Historiek tabel - UPDATED with temperature and humidity
class Historiek(BaseModel):
    HistoriekID: int
    DeviceID: int  # FIXED: was str, moet int zijn
    DrankType: str  
    Tijdstip: datetime
    Volume_Cola: Optional[float] = None  # FIXED: Added separate volumes
    Volume_Water: Optional[float] = None
    Temperatuur: Optional[float] = None  # NEW: Added temperature
    Vochtigheid: Optional[float] = None  # NEW: Added humidity


# Dagelijkse_Samenvatting tabel - UPDATED with temperature and humidity
class DagelijkseSamenvatting(BaseModel):
    SamenvattingID: int
    DeviceID: int  # FIXED: was str, moet int zijn
    Datum: date
    Aantal_Cola: int
    Aantal_Water: int
    Volume_Cola: float
    Volume_Water: float
    Temperatuur: Optional[int] = 20  # NEW: Added temperature (int for daily avg)
    Vochtigheid: Optional[int] = 50  # NEW: Added humidity (int for daily avg)
    
    # Computed properties (niet in database)
    @property
    def totaal_volume(self) -> float:
        return self.Volume_Cola + self.Volume_Water
    
    @property 
    def totaal_aantal(self) -> int:
        return self.Aantal_Cola + self.Aantal_Water


# Real-time sensor data (niet in database)
class SensorData(BaseModel):
    huidige_volume: float = 0
    totaal_volume: float = 0
    gewicht_glas: float = 0  # weight sensor
    aantal_keer_gebruikt: int = 0
    temperatuur: Optional[float] = None  # DHT11 temperature
    luchtvochtigheid: Optional[float] = None  # DHT11 humidity
    goal_percentage: float = 0
    afstand: Optional[float] = None  # ultrasonic sensor


# Voor drank registratie
class DrankRegistratie(BaseModel):
    type: str  # 'cola' or 'water'
    volume: float
    tijdstip: datetime
    temperatuur: Optional[float] = None
    vochtigheid: Optional[float] = None


class DTODrankRegistratie(BaseModel):
    type: str
    volume: float
    device_id: Optional[int] = 1
    temperatuur: Optional[float] = None
    vochtigheid: Optional[float] = None


# ===== REQUEST/RESPONSE MODELS voor API =====

class DTOSensorRequest(BaseModel):
    DeviceID: int  # FIXED: was str, moet int zijn


class DTOHistoriekRequest(BaseModel):
    DeviceID: int  # FIXED: was str, moet int zijn
    limit: int = 50


class SensorResponse(BaseModel):
    sensors: dict  # CHANGED: from SensorData to dict for flexibility
    timestamp: datetime = datetime.now()


class HistoriekResponse(BaseModel):
    DeviceID: int  # FIXED: was str, moet int zijn
    historiek: list  
    total_count: int


class SamenvattingResponse(BaseModel):
    DeviceID: int  # FIXED: was str, moet int zijn
    samenvatting: Optional[dict] = None  # CHANGED: from DagelijkseSamenvatting to dict
    datum: date


# ===== SOCKET.IO MODELS =====

class SocketMessage(BaseModel):
    event: str
    data: dict
    timestamp: datetime = datetime.now()


class DrankGeregistreerdMessage(BaseModel):
    type: str
    volume: float
    device_id: int
    tijdstip: datetime
    temperatuur: Optional[float] = None
    vochtigheid: Optional[float] = None


# ===== Debug =====

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime = datetime.now()


# ===== DATABASE RESPONSE MODELS =====

class DatabaseSamenvatting(BaseModel):
    """Model voor dagelijkse samenvatting zoals die uit database komt"""
    DeviceID: int
    Datum: date
    Aantal_Cola: int = 0
    Aantal_Water: int = 0
    Volume_Cola: float = 0.0
    Volume_Water: float = 0.0
    Temperatuur: int = 20
    Vochtigheid: int = 50


class DatabaseHistoriek(BaseModel):
    """Model voor historiek zoals die uit database komt"""
    HistoriekID: int
    DeviceID: int
    DrankType: str
    Tijdstip: datetime
    Volume_Cola: Optional[float] = None
    Volume_Water: Optional[float] = None
    Temperatuur: Optional[float] = None
    Vochtigheid: Optional[float] = None


# ===== SENSOR DATA MODELS =====

class CurrentSensorData(BaseModel):
    """Real-time sensor readings"""
    weight: float = 0.0 
    temperatuur: float = 20.0 
    humidity: float = 50.0  
    distance: float = 10.0  
    timestamp: datetime = datetime.now()


class SensorDataComplete(BaseModel):
    """Complete sensor data with statistics"""
    sensors: CurrentSensorData
    daily_stats: DatabaseSamenvatting
    timestamp: datetime = datetime.now()