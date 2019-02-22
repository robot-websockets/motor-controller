#!/usr/bin/python3
import RPi.GPIO as GPIO  # Import GPIO divers
import drive             # Import my Picocon 2 Motor controller
import argparse
import json
import time
import threading
import socketio
sio = socketio.Client()


print('motor controller starting...')

parser = argparse.ArgumentParser()
parser.add_argument('-W', '--ws_server')

args = parser.parse_args()

web_socket_server = "192.168.55.11"
if (args.ws_server):
    web_socket_server = args.ws_server


def set_up():
    # Set the GPIO pins mode - Also set in drive.py
    GPIO.setmode(GPIO.BOARD)
    # Turn GPIO warn off - CAN ALSO BE Set in drive.py
    GPIO.setwarnings(False)
    # Set the Front Trigger pin to output
    GPIO.setup(8, GPIO.OUT)
    GPIO.setup(10, GPIO.IN)    # Set the Front Echo pin to input
    drive.init()


def destroy():        # Shutdown GPIO and Cleanup modules
    print('\n... Shutting Down...\n')
    drive.stop()        # Make sure Bot is not moving when program exits
    drive.cleanup()     # Shutdown all motor control
    GPIO.cleanup()


class MotorController(threading.Thread):
    message = 'not running'
    direction = 'forwards'
    current_speed = 0
    requested_speed = 0
    ramp_speed = 1

    def __init__(self):
        super().__init__()

        self.running = True

    def run(self):
        while self.running:
            pass
            ##########################
            # code for controller here
            ##########################
            time.sleep(3)
            # print('Motor speed: {} direction: {} '.format(
            #     self.requested_speed, self.direction))

    def stop_running(self):
        self.running = False
        self.requested_speed = 0

    def start_running(self):
        self.running = True

    def ramp_speed(self, interval):
        self.ramp_speed = interval

    def set_message(self, message):
        self.message = message

    def move(self):
        if (self.direction == 'forwards'):
            if (self.requested_speed > 0):
                drive.forward(self.requested_speed)
            else:
                drive.stop()
        else:
            if (self.requested_speed > 0):
                drive.reverse(self.requested_speed)
            else:
                drive.stop()

    def set_speed(self, speed):
        self.requested_speed = speed
        print("speed is now: {}".format(speed))
        self.move()

    def set_direction(self, direction):
        self.direction = direction
        print("direction is now: {}".format(direction))
        self.move()

    def destroy(self):                 # Shutdown GPIO and Cleanup modules
        print('\n... Shutting Down...\n')
        drive.stop()        # Make sure Bot is not moving when program exits
        drive.cleanup()     # Shutdown all motor control
        GPIO.cleanup()


def motor_control(jsondata):
    min_speed = 50

    # when we receive data we need a minimum of 50
    # to move the train so we need to adjust the input
    # values accordinly.
    data = json.loads(jsondata)

    input_speed = int(data['speed'])
    train_speed = (input_speed/2) + min_speed

    # print('dir: {}  speed: {}'.format(data['direction'], data['speed']))

    Motor.set_speed(train_speed)
    Motor.set_direction(data['direction'])


@sio.on('connect')
def on_connect():
    print('Motor controller: connection established to the main server')


@sio.on('movement-control')
def on_movement_control(data):
    print('sio.on {}'.format(data))
    motor_control(data)


@sio.on('ping')  # we have connected. now send data about ourself
def on_con(data):
    # print('our serverId: ', data)
    sio.emit('ping', {'id': data,  'device': 'motor service'})


@sio.on('disconnect')
def on_disconnect():
    print('Motor controller: disconnected from server')
    # we have no connection, so wait 10 seconds and throw exception
    # to force a restart.
    time.sleep(10)
    raise Exception("Restart server connection lost")


# create a new  MotorController to use
try:
    set_up()  # start the motor driver
    Motor = MotorController()
    Motor.start()
    print('remote websocket server address: http://{}:5001:'
          .format(web_socket_server))

    # it just waits for the main server to start.
    time.sleep(5)
    sio.connect('http://{}:5001'.format(web_socket_server))
    sio.wait()
    #  anything here won't get executed.!!!
    #  while the program is running.
    destroy()  # probably not needed but it won't do any harm.


except KeyboardInterrupt:
    destroy()
    print('\n\n................... Exit .......................\n\n')
    exit(0)
