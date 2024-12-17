import socket
import RPi.GPIO as GPIO
import time
from picamera import PiCamera

GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 23
GPIO_ECHO = 24
BUZZER_PIN = 25
SOLENOID_PIN=17
camera = PiCamera()

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)
GPIO.setup(SOLENOID_PIN, GPIO.OUT)
GPIO.output(SOLENOID_PIN, GPIO.LOW)

server_ip = "192.168.43.115"
server_port = 1234

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

print("Distance monitoring client connected to {}:{}".format(server_ip, server_port))
print()

def send_data(distance):
    data = "Distance: {} cm".format(distance)
    print(data)
    client_socket.send(data.encode())
def measure_distance():
    GPIO.output(GPIO_TRIGGER, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, GPIO.LOW)

    pulse_start = time.time()
    pulse_end = time.time()

    while GPIO.input(GPIO_ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

try:
    while True:
        distance = measure_distance()
        print("Distance: {:.2f} cm".format(distance))
        time.sleep(1)
        if distance < 10:
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(BUZZER_PIN, GPIO.LOW)

            send_data(distance)
           # Take a picture using picamera
            image_path = '/home/sharath/Desktop/client1.jpg'
            camera.capture(image_path)
   
            break
        # Receive user message from the server
    user_message = client_socket.recv(1024).decode()
    while(user_message == "1"):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        GPIO.output(SOLENOID_PIN, GPIO.HIGH)
        time.sleep(3)
        print("Received user message from server:", user_message)
        break
    while(user_message == "0"):
        GPIO.output(SOLENOID_PIN, GPIO.LOW)

except KeyboardInterrupt:
    pass

client_socket.close()
GPIO.cleanup()
