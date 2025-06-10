import RPi.GPIO as GPIO
import time

TRIG = 19
ECHO = 18
BUTTON = 21  

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

stop_programma = False

def cleanup_gpio():
    print("\nGPIO wordt opgeruimd...")
    GPIO.cleanup()
    print("GPIO is opgeruimd.")

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

def wacht_op_knop(timeout=5):
    global stop_programma
    print(f"Wachten op knopdruk (max {timeout} seconden)...")
    start = time.perf_counter()

    while True:
        knop = GPIO.input(BUTTON)
        # Debug print om knopstatus te zien
        # print(f"DEBUG knopwaarde: {knop}")

        if knop == 0:
            print("Knop ingedrukt, doorgaan met schenken.")

            # Wacht tot knop wordt losgelaten, met timeout
            while GPIO.input(BUTTON) == 0:
                if time.perf_counter() - start > timeout:
                    print("Timeout bij loslaten knop, programma wordt beëindigd.")
                    stop_programma = True
                    return False
                time.sleep(0.01)

            return True

        if time.perf_counter() - start > timeout:
            print("Timeout verstreken zonder knopdruk, programma wordt beëindigd.")
            stop_programma = True
            return False

        time.sleep(0.01)

try:
    print("Beweging wordt gemeten... (CTRL+C om te stoppen)\n")
    while True:
        if stop_programma:
            break

        afstand = meet_afstand()
        if afstand is not None and 2 <= afstand <= 400:
            print(f"Afstand: {afstand:.1f} cm")
            if afstand <= 5:
                print("⚠️ Beweging gedetecteerd binnen 5 cm - pauzeer en wacht op knop.")
                if not wacht_op_knop(timeout=5):
                    break
        else:
            print("Meting ongeldig of buiten bereik")
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nMeten handmatig gestopt door gebruiker")
finally:
    cleanup_gpio()
    print("Programma beëindigd.")
