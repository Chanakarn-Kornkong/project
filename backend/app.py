import sys
import os
import asyncio
import socketio
import uvicorn
import logging
import RPi.GPIO as GPIO
import time
import Adafruit_DHT
from datetime import datetime, date, timedelta
import socket
import fcntl
import struct
from threading import Thread

from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.models import DagelijkseSamenvatting
from repositories.DataRepository import DataRepository

# ----------------------------------------------------
# Logging
# ----------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# ----------------------------------------------------
# Global Variables
# ----------------------------------------------------
sensor_active = False
active_drink = None
drink_counts = {"cola": 0, "water": 0}
last_button_time = {"cola": 0, "water": 0}
stop_programma = False

# LCD variabelen
lcd_display_index = 0
lcd_update_counter = 0
LCD_UPDATE_INTERVAL = 3  # Wissel elke 3 seconden tussen IP en klimaat
last_lcd_update = 0

# Sensor data cache
current_sensor_data = {
    'temperatuur': 0,
    'humidity': 0,
    'weight': 0,
    'distance': 0,
    'ip_address': None
}

# GPIO Pin Definitions
BUTTON_Cola = 16
BUTTON_Water = 20
TRIG = 19
ECHO = 18
BUTTON = 21
CLK = 24  
MISO = 23  
MOSI = 25  
CS = 12
DATA_PIN = 17
LCD_RS = 26
LCD_E = 13
LCD_D4 = 6
LCD_D5 = 5
LCD_D6 = 22
LCD_D7 = 27

# Sensor calibration
zero_offset = 0
scale_factor = 30.0

# ----------------------------------------------------
# GPIO Setup Functions
# ----------------------------------------------------
def setup_gpio():
    """Setup alle GPIO pins"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    try:
        # Knoppen
        GPIO.setup(BUTTON_Cola, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BUTTON_Water, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Ultrasonic sensor
        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN)
        GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # ADC
        GPIO.setup(CLK, GPIO.OUT)
        GPIO.setup(MOSI, GPIO.OUT)
        GPIO.setup(MISO, GPIO.IN)
        GPIO.setup(CS, GPIO.OUT)
        # LCD
        for pin in [LCD_RS, LCD_E, LCD_D4, LCD_D5, LCD_D6, LCD_D7]:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)
        GPIO.output(CS, True)
        GPIO.output(CLK, False)
        logger.info("GPIO geïnitialiseerd")
    except Exception as e:
        logger.error(f"GPIO init error: {e}")

def cleanup_gpio():
    logger.info("GPIO wordt opgeruimd...")
    try:
        GPIO.cleanup()
        logger.info("GPIO is opgeruimd.")
    except Exception as e:
        logger.error(f"GPIO cleanup error: {e}")

# ----------------------------------------------------
# Database Functions - FIXED VERSIONS
# ----------------------------------------------------
def save_drink_to_database(DrankType, Volume, Temperatuur=None, Vochtigheid=None, device_id=1):
    """
    GEFIXTE versie - gebruik DataRepository.save_drink_complete
    """
    try:
        return DataRepository.save_drink_complete(device_id, DrankType, Volume, Temperatuur, Vochtigheid)
    except Exception as ex:
        print(f"Fout bij opslaan naar database: {ex}")
        return False

# ----------------------------------------------------
# Sensor Functions
# ----------------------------------------------------
def bereken_volume_uit_afstand(afstand):
    """Bereken volume op basis van afstand (cilindervormig glas)"""
    glas_hoogte = 15  # cm
    glas_radius = 3   
    
    if afstand >= glas_hoogte:
        return 0  
    
    water_hoogte = glas_hoogte - afstand
    volume_ml = 3.14159 * (glas_radius ** 2) * water_hoogte
    return round(volume_ml, 0)

def check_drink_buttons():
    """Check knoppen voor het activeren van sensoren"""
    global drink_counts, last_button_time, sensor_active, active_drink
    
    current_time = time.time()
    
    # Check cola knop
    if GPIO.input(BUTTON_Cola) == 0:
        if current_time - last_button_time["cola"] > 0.5:  # 500ms debounce
            drink_counts["cola"] += 1
            last_button_time["cola"] = current_time
            sensor_active = True
            active_drink = "cola"
            print(f"\n🥤 COLA knop ingedrukt! (Totaal: {drink_counts['cola']})")
            print("=" * 50)
            return True
    
    # Check water knop
    if GPIO.input(BUTTON_Water) == 0:
        if current_time - last_button_time["water"] > 0.5:  # 500ms debounce
            drink_counts["water"] += 1
            last_button_time["water"] = current_time
            sensor_active = True
            active_drink = "water"
            print(f"\n WATER knop ingedrukt! (Totaal: {drink_counts['water']})")
            print("=" * 50)
            return True
    
    return False

def get_drink_stats():
    """Geef drankstatistieken terug"""
    return drink_counts.copy()

# ----------------------------------------------------
# LCD Functions
# ----------------------------------------------------
def lcd_toggle_enable():
    time.sleep(0.0005)
    GPIO.output(LCD_E, True)
    time.sleep(0.0005)
    GPIO.output(LCD_E, False)
    time.sleep(0.0005)

def lcd_send_nibble(data):
    GPIO.output(LCD_D4, data & 0x01)
    GPIO.output(LCD_D5, data & 0x02)
    GPIO.output(LCD_D6, data & 0x04)
    GPIO.output(LCD_D7, data & 0x08)
    lcd_toggle_enable()

def lcd_send_byte(data, mode):
    GPIO.output(LCD_RS, mode)
    lcd_send_nibble(data >> 4)
    lcd_send_nibble(data & 0x0F)
    time.sleep(0.001)

def lcd_init():
    time.sleep(0.02)
    lcd_send_nibble(0x03)
    time.sleep(0.005)
    lcd_send_nibble(0x03)
    time.sleep(0.005)
    lcd_send_nibble(0x03)
    time.sleep(0.005)
    lcd_send_nibble(0x02)

    lcd_send_byte(0x28, False)  # 4-bit mode, 2 lines
    lcd_send_byte(0x0C, False)  # Display on, cursor off
    lcd_send_byte(0x06, False)  # Entry mode
    lcd_send_byte(0x01, False)  # Clear display
    time.sleep(0.005)

def lcd_clear():
    lcd_send_byte(0x01, False)
    time.sleep(0.005)

def lcd_set_cursor(col, row):
    if row == 0:
        lcd_send_byte(0x80 + col, False)
    elif row == 1:
        lcd_send_byte(0xC0 + col, False)

def lcd_message(text):
    for char in text:
        lcd_send_byte(ord(char), True)

def lcd_display_two_lines(line1, line2):
    lcd_clear()
    lcd_set_cursor(0, 0)
    lcd_message(line1[:16])
    lcd_set_cursor(0, 1)
    lcd_message(line2[:16])

def update_idle_lcd_display():
    """Update LCD met wisselende display tussen IP en klimaat"""
    global lcd_display_index, last_lcd_update
    
    current_time = time.time()
    
    # Wissel elke LCD_UPDATE_INTERVAL seconden
    if current_time - last_lcd_update >= LCD_UPDATE_INTERVAL:
        try:
            if lcd_display_index == 0:
                # Toon IP adres
                ip_address = current_sensor_data.get('ip_address', '0.0.0.0')
                lcd_display_two_lines("IP", f"{ip_address}")
                lcd_display_index = 1
            else:
                # Toon temperatuur en vochtigheid
                temp = current_sensor_data.get('temperatuur', 0)
                humidity = current_sensor_data.get('humidity', 0)
                lcd_display_two_lines(f"Temp: {temp}C", f"Humid: {humidity}%")
                lcd_display_index = 0
            
            last_lcd_update = current_time
            
        except Exception as e:
            logger.error(f"LCD update error: {e}")

# ----------------------------------------------------
# Network Functions
# ----------------------------------------------------
def get_ip_address():
    try:
        # Probeer eerst wlan0 (wifi)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip = fcntl.ioctl(
                s.fileno(),
                0x8915,
                struct.pack('256s', b'wlan0')
            )[20:24]
            s.close()
            return socket.inet_ntoa(ip)
        except Exception:
            pass

        # Probeer eth0 (ethernet)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip = fcntl.ioctl(
                s.fileno(),
                0x8915,
                struct.pack('256s', b'eth0')
            )[20:24]
            s.close()
            return socket.inet_ntoa(ip)
        except Exception:
            pass

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            fallback_ip = s.getsockname()[0]
            s.close()
            return fallback_ip
        except Exception:
            return "127.0.0.1"
    except Exception as e:
        print(f"Geen IP kunnen bepalen: {e}")
        return "127.0.0.1"

# ----------------------------------------------------
# Ultrasonic Sensor Functions
# ----------------------------------------------------
def meet_afstand():
    GPIO.output(TRIG, False)
    time.sleep(0.05)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    timeout = time.perf_counter() + 0.04
    while GPIO.input(ECHO) == 0:
        if time.perf_counter() > timeout:
            return None
    start = time.perf_counter()

    timeout = time.perf_counter() + 0.04
    while GPIO.input(ECHO) == 1:
        if time.perf_counter() > timeout:
            return None
    end = time.perf_counter()

    duur = end - start
    afstand = (duur * 34300) / 2
    return afstand

def wacht_op_knop(timeout=10):
    """Wacht op BEVESTIG knopdruk (pin 21) - GEFIXTE versie"""
    print(f"Wachten op BEVESTIG knop (pin 21) - max {timeout} seconden...")
    start = time.perf_counter()

    while True:
        knop = GPIO.input(BUTTON) 

        if knop == 0:  # Knop ingedrukt
            print("BEVESTIG knop ingedrukt!")
            
            # Meet volume én klimaat data
            afstand = meet_afstand()
            if afstand is not None:
                volume = bereken_volume_uit_afstand(afstand)
                if volume > 0:
                    print(f"Gemeten volume: {volume}ml")
                    
                    # temperatuur en vochtigheid
                    temperatuur, vochtigheid = read_dht11()
                    print(f"Klimaat: {temperatuur}°C, {vochtigheid}%")
                    
                    if save_drink_to_database(active_drink, volume, temperatuur, vochtigheid, device_id=1):
                        print("Data succesvol opgeslagen in database!")
                    else:
                        print("Fout bij opslaan in database")
                else:
                    print("Geen volume gedetecteerd")
            else:
                print("Kon afstand niet meten")
            
            # Debounce
            release_start = time.perf_counter()
            while GPIO.input(BUTTON) == 0:
                if time.perf_counter() - release_start > 3:
                    print("Knop te lang ingedrukt, ga verder...")
                    break
                time.sleep(0.01)
            
            return True

        if time.perf_counter() - start > timeout:
            print("Timeout bereikt - geen bevestiging ontvangen")
            return False

        time.sleep(0.01)

# ----------------------------------------------------
# ADC Weight Sensor Functions
# ----------------------------------------------------
def read_adc(channel):
    if channel < 0 or channel > 7:
        return -1

    GPIO.output(CS, False)

    command = 0x18 | channel
    for i in range(5):
        GPIO.output(MOSI, (command & 0x10) != 0)
        command <<= 1
        GPIO.output(CLK, True)
        GPIO.output(CLK, False)

    GPIO.output(CLK, True)
    GPIO.output(CLK, False)

    result = 0
    for i in range(10):
        GPIO.output(CLK, True)
        result <<= 1
        if GPIO.input(MISO):
            result |= 1
        GPIO.output(CLK, False)

    GPIO.output(CS, True)
    return result

def read_average(channel, samples=60):
    total = 0
    for _ in range(samples):
        reading = read_adc(channel)
        if reading != -1:
            total += reading
        time.sleep(0.005)
    return total / samples

def adc_to_voltage(adc_value):
    return (adc_value / 1023.0) * 3.3

def voltage_to_resistance(voltage, r_fixed=10000):
    if voltage <= 0.001:
        return 999999
    return r_fixed * (3.3 - voltage) / voltage

def resistance_to_force_max_sensitive(resistance):
    if resistance >= 15000:
        return 0
    elif resistance >= 14000:
        return 100 * (15000 - resistance) / 1000
    elif resistance >= 12000:
        return 200 + 300 * (14000 - resistance) / 2000
    elif resistance >= 8000:
        return 500 + 1000 * (12000 - resistance) / 4000
    elif resistance >= 4000:  
        return 1500 + 2500 * (8000 - resistance) / 4000
    else:
        return 4000 + 4000 * max(0, (4000 - resistance)) / 4000

# ----------------------------------------------------
# DHT11 Temperature/Humidity Sensor
# ----------------------------------------------------
def read_dht11():
    data = []

    GPIO.setup(DATA_PIN, GPIO.OUT)
    GPIO.output(DATA_PIN, GPIO.HIGH)
    time.sleep(0.05)  

    GPIO.output(DATA_PIN, GPIO.LOW)
    time.sleep(0.02)  

    GPIO.output(DATA_PIN, GPIO.HIGH)
    time.sleep(0.00004)  

    GPIO.setup(DATA_PIN, GPIO.IN)

    count = 0
    while GPIO.input(DATA_PIN) == GPIO.HIGH:
        count += 1
        if count > 100000:
            print("Timeout: sensor reageert niet (blijft HIGH)")
            return None, None

    while GPIO.input(DATA_PIN) == GPIO.LOW:
        count += 1
        if count > 100000:
            print("Timeout: sensor blijft LOW")
            return None, None

    for i in range(40):
        while GPIO.input(DATA_PIN) == GPIO.LOW:
            pass

        start = time.time()
        while GPIO.input(DATA_PIN) == GPIO.HIGH:
            pass

        duration = time.time() - start

        bit = 1 if duration > 0.00005 else 0
        data.append(bit)

    bytes_ = []
    for i in range(0, 40, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | data[i + j]
        bytes_.append(byte)

    humidity = bytes_[0]
    temperatuur = bytes_[2]
    checksum = bytes_[4]
    if (bytes_[0] + bytes_[1] + bytes_[2] + bytes_[3]) & 0xFF == checksum:
        return temperatuur, humidity
    else:
        print("Checksum mismatch – ongeldige data.")
        return None, None

# ----------------------------------------------------
# Sensor Monitoring Functions
# ----------------------------------------------------
def read_single_sensor_cycle():
    """Lees één cyclus van alle sensoren uit"""
    sensor_data = {}
    
    # Ultrasonic sensor
    afstand = meet_afstand()
    if afstand is not None and 2 <= afstand <= 400:
        sensor_data['distance'] = afstand
        print(f"Afstand: {afstand:.1f} cm")
    else:
        sensor_data['distance'] = None
        print("Afstand: Ongeldig")

    # Gewichtssensor
    adc_value = read_average(0, samples=20)
    voltage = adc_to_voltage(adc_value)
    resistance = voltage_to_resistance(voltage)
    weight = resistance_to_force_max_sensitive(resistance)
    weight = max(0, (weight - zero_offset) * scale_factor)
    sensor_data['weight'] = int(weight)
    print(f"Gewicht: {int(weight)} g")

    # Temperatuur en luchtvochtigheid (niet elke cyclus voor snelheid)
    if time.time() % 3 < 1:
        temperatuur, luchtvochtigheid = read_dht11()
        if temperatuur is not None and luchtvochtigheid is not None:
            sensor_data['temperatuur'] = temperatuur
            sensor_data['humidity'] = luchtvochtigheid
            print(f"Temperatuur: {temperatuur}°C")
            print(f"Luchtvochtigheid: {luchtvochtigheid}%")
        else:
            sensor_data['temperatuur'] = None
            sensor_data['humidity'] = None
            print("Klimaat: Niet beschikbaar")
    
    return sensor_data

def continuous_sensor_monitoring():
    """Blijf sensoren monitoren totdat beweging wordt gedetecteerd"""
    print(f"START CONTINUE MONITORING VOOR {active_drink.upper()}")
    print("Sensoren draaien continu...")
    print("Wachtend op beweging (≤5cm)")
    print("Druk Ctrl+C om te stoppen")
    print("-" * 50)
    
    cycle_count = 0
    
    while True:
        cycle_count += 1
        print(f"\nCyclus #{cycle_count} - {active_drink.upper()} modus:")
        
        sensor_data = read_single_sensor_cycle()
        
        # Check of er beweging is gedetecteerd
        if sensor_data.get('distance') is not None:
            if sensor_data['distance'] <= 5:
                print("\nBEWEGING GEDETECTEERD! (≤5cm)")
                print("Druk op de BEVESTIG knop (pin 21) om door te gaan...")
                
                # Wacht op bevestigingsknop
                knop_success = wacht_op_knop(timeout=10)
                
                if knop_success:
                    print("Bevestiging ontvangen! Schenken voltooid!")
                    break
                else:
                    print("Timeout - geen bevestiging, ga verder met monitoren...")
                    continue
        
        # Update LCD met sensor data tijdens monitoring (gewicht)
        if sensor_data.get('weight') is not None:
            weight_str = f"{sensor_data['weight']}g"
            lcd_display_two_lines(f"{active_drink.upper()} actief", f"Gewicht: {weight_str}")
        
        print("-" * 30)
        time.sleep(1)

# ----------------------------------------------------
# Hardware Monitoring Thread
# ----------------------------------------------------
def hardware_monitoring_thread():
    """Achtergrond thread voor hardware monitoring"""
    logger.info("🔧 Hardware monitoring thread gestart")
    
    while not stop_programma:
        try:
            if check_drink_buttons():
                logger.info(f"Knop gedetecteerd voor {active_drink}")
                
                # Start sensor monitoring
                continuous_sensor_monitoring()
                
                # Reset sensor active state
                global sensor_active
                sensor_active = False
            else:
                if not sensor_active:
                    update_idle_lcd_display()
            
            time.sleep(0.1)  # Kleine pauze om CPU te sparen
            
        except Exception as e:
            logger.error(f"Hardware monitoring error: {e}")
            time.sleep(1)
    
    logger.info(" Hardware monitoring thread gestopt")

# ----------------------------------------------------
# Async Helper Functions
# ----------------------------------------------------
async def lees_alle_sensoren():
    """Lees alle sensoren - ECHTE sensor integratie"""
    try:
        sensor_data = {}
        
        # Ultrasonic sensor
        afstand = meet_afstand()
        if afstand is not None and 2 <= afstand <= 400:
            sensor_data['distance'] = round(afstand, 1)
        else:
            sensor_data['distance'] = 0.0
        
        # Gewichtssensor
        try:
            adc_value = read_average(0, samples=10)  # Minder samples voor snelheid
            voltage = adc_to_voltage(adc_value)
            resistance = voltage_to_resistance(voltage)
            weight = resistance_to_force_max_sensitive(resistance)
            weight = max(0, (weight - zero_offset) * scale_factor)
            sensor_data['weight'] = int(weight)
        except Exception as e:
            logger.error(f"Weight sensor error: {e}")
            sensor_data['weight'] = 0
        
        # DHT11 temperatuur en luchtvochtigheid (niet elke keer voor snelheid)
        try:
            temperatuur, luchtvochtigheid = read_dht11()
            if temperatuur is not None and luchtvochtigheid is not None:
                sensor_data['temperatuur'] = temperatuur
                sensor_data['temperature'] = temperatuur  # Beide voor compatibiliteit
                sensor_data['humidity'] = luchtvochtigheid
                
                # Update global cache
                current_sensor_data['temperatuur'] = temperatuur
                current_sensor_data['humidity'] = luchtvochtigheid
            else:
                # Gebruik cached waardes als sensor faalt
                sensor_data['temperatuur'] = current_sensor_data.get('temperatuur', 20.0)
                sensor_data['temperature'] = current_sensor_data.get('temperatuur', 20.0)
                sensor_data['humidity'] = current_sensor_data.get('humidity', 50.0)
        except Exception as e:
            logger.error(f"DHT11 sensor error: {e}")
            sensor_data['temperatuur'] = 20.0
            sensor_data['temperature'] = 20.0
            sensor_data['humidity'] = 50.0
        
        # Update global cache
        current_sensor_data.update(sensor_data)
        
        return sensor_data
        
    except Exception as e:
        logger.error(f"Fout bij lezen sensoren: {e}")
        return {
            'weight': 0.0,
            'temperatuur': 20.0,
            'temperature': 20.0,
            'humidity': 50.0,
            'distance': 0.0
        }

async def sensor_heartbeat():
    """Stuur elke 2 seconden sensor data naar alle clients"""
    while not stop_programma:
        try:
            sensor_data = await lees_alle_sensoren()
            await sio.emit('B2F_sensor_data', {'sensors': sensor_data})
            await asyncio.sleep(20)
        except Exception as e:
            logger.error(f"Sensor heartbeat error: {e}")
            await asyncio.sleep(20)
# ----------------------------------------------------
# Aan/Uit knop
# ----------------------------------------------------


#Onder constructie 


# ----------------------------------------------------
# FastAPI Setup
# ----------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup en shutdown events"""
    # Startup
    logger.info(" GlasGo! is starting up")
    setup_gpio()
    
    # Setup LCD
    try:
        lcd_init()
        lcd_display_two_lines("System Starting", "Loading....")
        logger.info(" LCD geïnitialiseerd")
    except Exception as e:
        logger.error(f"LCD init error: {e}")
    
    # Setup database
    if DataRepository.setup_tables():
        logger.info(" Database tables ready")
        DataRepository.insert_test_data()
    else:
        logger.error(" Database setup failed")
    
    # Toon IP adres op LCD en sla op in cache
    try:
        ip_address = get_ip_address()
        current_sensor_data['ip_address'] = ip_address
        lcd_display_two_lines("Server Ready", f"IP: {ip_address}")
        logger.info(f" Server klaar op IP: {ip_address}")
    except Exception as e:
        logger.error(f"IP setup error: {e}")
    
    # Lees initiële klimaat data voor LCD
    try:
        temp, humidity = read_dht11()
        if temp is not None and humidity is not None:
            current_sensor_data['temperatuur'] = temp
            current_sensor_data['humidity'] = humidity
        else:
            current_sensor_data['temperatuur'] = 20
            current_sensor_data['humidity'] = 50
    except Exception as e:
        logger.error(f"Initial climate read error: {e}")
        current_sensor_data['temperatuur'] = 20
        current_sensor_data['humidity'] = 50
    
    # Start hardware monitoring thread
    global stop_programma
    stop_programma = False
    hardware_thread = Thread(target=hardware_monitoring_thread, daemon=True)
    hardware_thread.start()
    logger.info(" Hardware monitoring thread gestart")
    
    # Start sensor heartbeat
    asyncio.create_task(sensor_heartbeat())
    logger.info(" Sensor heartbeat gestart")
    
    yield
    
    # Shutdown
    logger.info(" Shutting down Smart Drink Tracker...")
    stop_programma = True
    cleanup_gpio()

app = FastAPI(lifespan=lifespan, title="Smart Drink Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Socket.IO setup
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi', logger=True)
sio_app = socketio.ASGIApp(sio, app)

ENDPOINT = "/api/v1"

# ----------------------------------------------------
# FastAPI Routes
# ----------------------------------------------------
@app.get("/")
async def root():
    return {"message": "Smart Drink Tracker Server actief!", "status": "running"}

@app.get("/routes")
async def get_routes():
    return {
        "available_routes": [
            {"path": route.path, "name": route.name, "methods": list(route.methods)} 
            for route in app.routes if hasattr(route, 'methods')
        ]
    }
@app.get(ENDPOINT + "/sensors")
async def get_sensor_data():
    """Haal huidige sensor data op"""
    try:
        sensor_data = await lees_alle_sensoren()
        return {"sensors": sensor_data, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Fout bij ophalen sensor data: {e}")
        return {"sensors": {}, "error": str(e)}

@app.get(ENDPOINT + "/historiek/{device_id}")
async def get_historiek(device_id: int):
    """Haal historiek op voor een device"""
    try:
        historiek = DataRepository.get_historiek(device_id)
        return {
            "device_id": device_id, 
            "historiek": historiek, 
            "total_count": len(historiek)
        }
    except Exception as e:
        logger.error(f"Fout bij ophalen historiek: {e}")
        return {"error": "Fout bij ophalen historiek", "device_id": device_id}

@app.get(ENDPOINT + "/samenvatting/{device_id}")
async def get_dagelijkse_samenvatting(device_id: int):
    """Haal dagelijkse samenvatting op"""
    try:
        vandaag = date.today()
        samenvatting = DataRepository.read_samenvatting(device_id, vandaag)
        
        logger.info(f"Samenvatting opgehaald voor device {device_id}")
        return {"samenvatting": samenvatting, "datum": vandaag.isoformat()}
        
    except Exception as e:
        logger.error(f"Fout bij ophalen samenvatting: {e}")
        return {"error": "Fout bij ophalen samenvatting", "samenvatting": None}

@app.post(ENDPOINT + "/drink")
async def manual_drink_registration(drink_data: dict):
    """Handmatige drink registratie - GEFIXTE versie"""
    try:
        drink_type = drink_data.get('type', '').lower()
        volume = float(drink_data.get('volume', 0))
        device_id = int(drink_data.get('device_id', 1))
        temperatuur = drink_data.get('temperatuur', None)  
        vochtigheid = drink_data.get('vochtigheid', None)  
        
        if drink_type in ['cola', 'water'] and volume > 0:
            success = DataRepository.save_drink_complete(device_id, drink_type, volume, temperatuur, vochtigheid)
            
            if success:
                await sio.emit('B2F_drank_geregistreerd', {
                    'type': drink_type,
                    'volume': volume,
                    'device_id': device_id,
                    'tijdstip': datetime.now().isoformat(),
                    'temperatuur': temperatuur,
                    'vochtigheid': vochtigheid
                })
                
                logger.info(f"Drink geregistreerd: {drink_type} {volume}ml voor device {device_id}")
                return {"success": True, "message": f"{drink_type} geregistreerd: {volume}ml"}
        
        return {"success": False, "message": "Ongeldige drink data"}
        
    except Exception as e:
        logger.error(f"Fout bij handmatige drink registratie: {e}")
        return {"success": False, "error": str(e)}

# ----------------------------------------------------
# Socket.IO Events
# ----------------------------------------------------
@sio.event
async def connect(sid, environ):
    logger.info(f"🔌 Client geconnecteerd: {sid}")
    try:
        # Stuur direct sensor data bij verbinding
        sensor_data = await lees_alle_sensoren()
        await sio.emit('B2F_sensor_data', {'sensors': sensor_data}, to=sid)
        
        # Stuur ook stats
        vandaag = date.today()
        samenvatting = DataRepository.read_samenvatting(1, vandaag)
        await sio.emit('B2F_stats_data', {'stats': samenvatting}, to=sid)
        
    except Exception as e:
        logger.error(f"Fout bij client connect: {e}")

@sio.event
async def disconnect(sid):
    logger.info(f"🔌 Client gedisconnecteerd: {sid}")

@sio.event
async def F2B_request_sensor_data(sid, data=None):
    """Client vraagt om sensor data"""
    try:
        sensor_data = await lees_alle_sensoren()
        logger.info(f"Sensor data request van {sid}: {sensor_data}")
        await sio.emit('B2F_sensor_data', {'sensors': sensor_data}, to=sid)
    except Exception as e:
        logger.error(f"Fout bij sensor data request: {e}")

@sio.event
async def F2B_request_stats(sid, data=None):
    """Client vraagt om statistieken"""
    try:
        vandaag = date.today()
        device_id = 1  # Default
        
        if data and isinstance(data, dict) and "device_id" in data:
            try:
                device_id = int(data["device_id"])
            except (ValueError, TypeError):
                logger.warning(f"Invalid device_id in request: {data.get('device_id')}")
        
        logger.info(f"Stats request van {sid} voor device_id={device_id} op {vandaag}")
        
        samenvatting = DataRepository.read_samenvatting(device_id, vandaag)
        
        logger.info(f"B2F_stats_data emit naar {sid}: {samenvatting}")  
        await sio.emit('B2F_stats_data', {'stats': samenvatting}, to=sid)
        
    except Exception as e:
        logger.error(f"Fout bij stats request: {e}")
        await sio.emit('B2F_stats_data', {'stats': None}, to=sid)

@sio.event
async def F2B_test_drink(sid, data=None):
    """Test event voor drink registratie vanaf frontend - GEFIXTE versie"""
    try:
        drink_type = data.get('type', 'water') if data else 'water'
        volume = data.get('volume', 250) if data else 250
        device_id = data.get('device_id', 1) if data else 1
        temperatuur = data.get('temperatuur', 22.0) if data else 22.0
        vochtigheid = data.get('vochtigheid', 55.0) if data else 55.0
        
        success = DataRepository.save_drink_complete(device_id, drink_type, volume, temperatuur, vochtigheid)
        
        if success:
            await sio.emit('B2F_drank_geregistreerd', {
                'type': drink_type,
                'volume': volume,
                'device_id': device_id,
                'tijdstip': datetime.now().isoformat(),
                'temperatuur': temperatuur,
                'vochtigheid': vochtigheid
            })
            
            vandaag = date.today()
            samenvatting = DataRepository.read_samenvatting(device_id, vandaag)
            await sio.emit('B2F_stats_data', {'stats': samenvatting})
            
            logger.info(f"Test drink succesvol: {drink_type} {volume}ml")
        else:
            logger.error("Test drink registratie mislukt")
            
    except Exception as e:
        logger.error(f"Fout bij test drink: {e}")

# ----------------------------------------------------
# Main Hardware Loop (Optional - voor hardware testing)
# ----------------------------------------------------
def run_hardware_loop():
    """Optionele hardware loop voor standalone testing"""
    global stop_
# ----------------------------------------------------
# Run the server
# ----------------------------------------------------
if __name__ == "__main__":
    try:
        logger.info("🚀 Starting Smart Drink Tracker Server...")
        uvicorn.run(
            "app:sio_app", 
            host="0.0.0.0",  
            port=5501, 
            log_level="info", 
            reload=False
        )
        
    except KeyboardInterrupt:
        logger.info(" Server gestopt door gebruiker")
    except Exception as e:
        logger.error(f" Server fout: {e}")
    finally:
        logger.info(" Server afgesloten")