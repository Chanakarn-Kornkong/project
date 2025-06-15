import RPi.GPIO as GPIO
import time

DATA_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

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
            return None


    while GPIO.input(DATA_PIN) == GPIO.LOW:
        count += 1
        if count > 100000:
            print("Timeout: sensor blijft LOW")
            return None


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
    temperature = bytes_[2]
    checksum = bytes_[4]
    if (bytes_[0] + bytes_[1] + bytes_[2] + bytes_[3]) & 0xFF == checksum:
        print(f"Temp: {temperature}°C  |  Hum: {humidity}%")
    else:
        print("Checksum mismatch – ongeldige data.")

try:
    while True:
        read_dht11()
        time.sleep(2)
except KeyboardInterrupt:
    GPIO.cleanup()