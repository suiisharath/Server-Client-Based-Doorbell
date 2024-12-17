import socket
import RPi.GPIO as GPIO
import time
import picamera

GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 23
GPIO_ECHO = 24
BUZZER_PIN = 25

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)

server_ip = "192.168.43.252"
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
        if distance < 10:
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(BUZZER_PIN, GPIO.LOW)

            # Take a picture using picamera
            with picamera.PiCamera() as camera:
                camera.resolution = (1024, 768)
                camera.capture('/home/pi/Pictures/client2.jpg')
            send_data(distance)
            break

        # Receive user message from the server
        user_message = client_socket.recv(1024).decode()

        if user_message == "1":
            GPIO.output(SOLENOID_PIN, GPIO.HIGH)
        elif user_message == "0":
            GPIO.output(SOLENOID_PIN, GPIO.LOW)

except KeyboardInterrupt:
    pass

client_socket.close()
GPIO.cleanup()
