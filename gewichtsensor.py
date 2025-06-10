import RPi.GPIO as GPIO
import time

CLK  = 24  
MISO = 23  
MOSI = 25  
CS   = 12   

GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(MOSI, GPIO.OUT)
GPIO.setup(MISO, GPIO.IN)
GPIO.setup(CS, GPIO.OUT)

GPIO.output(CS, True)
GPIO.output(CLK, False)

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
        time.sleep(0.005)  # kort wachten voor stabielere waarden
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

zero_offset = 0
scale_factor = 30.0  # flink verhoogd voor maximale gevoeligheid

print("RP-S40-ST Gewichtssensor - Maximale gevoeligheid")
print("Druk Ctrl+C om te stoppen\n")

try:
    while True:
        adc_value = read_average(0, samples=60)
        voltage = adc_to_voltage(adc_value)
        resistance = voltage_to_resistance(voltage)
        
        weight = resistance_to_force_max_sensitive(resistance)
        weight = max(0, (weight - zero_offset) * scale_factor)
        
        print(f"Gewicht: {int(weight)} g")
        time.sleep(0.3)

except KeyboardInterrupt:
    print("\nGestopt.")
finally:
    GPIO.cleanup()
