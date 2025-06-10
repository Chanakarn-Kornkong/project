import RPi.GPIO as GPIO
import time
import socket
import fcntl
import struct

LCD_RS = 26
LCD_E  = 13
LCD_D4 = 6
LCD_D5 = 5
LCD_D6 = 22
LCD_D7 = 27

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
    GPIO.setmode(GPIO.BCM)
    for pin in [LCD_RS, LCD_E, LCD_D4, LCD_D5, LCD_D6, LCD_D7]:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, False)

    time.sleep(0.02)
    lcd_send_nibble(0x03)
    time.sleep(0.005)
    lcd_send_nibble(0x03)
    time.sleep(0.005)
    lcd_send_nibble(0x03)
    time.sleep(0.005)
    lcd_send_nibble(0x02)

    lcd_send_byte(0x28, False)
    lcd_send_byte(0x0C, False)
    lcd_send_byte(0x06, False)
    lcd_send_byte(0x01, False)
    time.sleep(0.005)

def lcd_message(text):
    for char in text:
        lcd_send_byte(ord(char), True)

def get_ip_address(interface):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = fcntl.ioctl(
            s.fileno(),
            0x8915, 
            struct.pack('256s', interface[:15].encode('utf-8'))
        )[20:24]
        return socket.inet_ntoa(ip)
    except OSError:
        return "Geen IP"


INTERFACE_NAME = "eth0"

try:
    lcd_init()
    lcd_send_byte(0x01, False)
    time.sleep(0.005)

    ip = get_ip_address(INTERFACE_NAME)

    lcd_send_byte(0x80, False)      
    lcd_message("Ip a")             
    lcd_send_byte(0xC0, False)      
    lcd_message(ip)                 

    time.sleep(10)

finally:
    GPIO.cleanup()
