import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

led_pin = 20
GPIO.setup(led_pin, GPIO.OUT)

try:
    while True:
        GPIO.output(led_pin, GPIO.HIGH)  # LED aan
        print("LED aan")
        time.sleep(1)                   # 1 seconde wachten

        GPIO.output(led_pin, GPIO.LOW)   # LED uit
        print("LED uit")
        time.sleep(1)                   # 1 seconde wachten
except KeyboardInterrupt:
    print("Programma gestopt")

finally:
    GPIO.cleanup()  # Zet alle GPIO's terug naar input (veilig afsluiten)
