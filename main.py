#!/usr/bin/python3
import RPi.GPIO as GPIO  # Import GPIO divers
import drive             # Import my Picocon 2 Motor controller
import argparse
import json
import time
import threading
import socketio
sio = socketio.Client()

port = 5001
web_socket_server = "192.168.55.1"
debug = False
min_speed = 40

train_object_too_close = False
train_movement_started = False


print('motor controller starting...')

parser = argparse.ArgumentParser()
parser.add_argument('-S', '--server')
parser.add_argument('-P', '--port')
parser.add_argument('-M', '--min')
parser.add_argument('-D', '--debug')

args = parser.parse_args()

if (args.server):
    server_url = args.server

if (args.port):
    port = args.port

if (args.min):
    min_speed = int(args.min)

if (args.debug):
    res = (args.debug).lower()
    if res == "false":
        debug = False
    elif res == "true":
        debug = True
# we should now have the info we need
full_url = 'http://{}:{}'.format(server_url, port)


def set_up():
    # Set the GPIO pins mode - Also set in drive.py
    GPIO.setmode(GPIO.BOARD)
    # Turn GPIO warn off - CAN ALSO BE Set in drive.py
    GPIO.setwarnings(False)
    # Set the Front Trigger pin to output
    # GPIO.setup(8, GPIO.OUT)
    # GPIO.setup(10, GPIO.IN)    # Set the Front Echo pin to input
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
    # ramp_speed = 1
    proximity_set_speed = 0
    min_speed = 40

    def __init__(self):
        super().__init__()

        self.running = True

        print('min speed:', self.min_speed)

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
        if (self.direction == 'backwards'):
            if (self.requested_speed > 0):
                drive.reverse(self.requested_speed)
            else:
                drive.stop()
        else:
            if (self.requested_speed > 0):
                drive.forward(self.requested_speed)
            else:
                drive.stop()

    def set_speed(self, speed):
        self.requested_speed = speed
        # print("speed is now: {}".format(speed))
        self.move()

    def set_direction(self, direction):
        self.direction = direction.lower()
        print("direction is now: {}".format(direction))
        self.move()

    def destroy(self):                 # Shutdown GPIO and Cleanup modules
        print('\n... Shutting Down...\n')
        drive.stop()        # Make sure Bot is not moving when program exits
        drive.cleanup()     # Shutdown all motor control
        GPIO.cleanup()


def calculate_motor_speed(speed):

    if int(speed) is 0:
        return 0
    target_speed = int(((100 - min_speed)/100*speed) + min_speed)
    print('target speed:', target_speed)
    return target_speed


def motor_control(jsondata):
    global train_movement_started

    # when we receive data we need a minimum of 50
    # to move the motor so we need to adjust the input
    # values accordinly.
    data = json.loads(jsondata)
    motor_speed = calculate_motor_speed(int(data['speed']))

    if debug:
        print('dir: {}  speed: {}'.format(data['direction'], data['speed']))

    Motor.set_direction(data['direction'])

    # used if proximity sensor changes speed.
    Motor.current_speed = motor_speed
    Motor.set_speed(motor_speed)

    if motor_speed == 0:
        print('train stopped')
        train_movement_started = False
        message1 = 'Movement Stopped @ {}'.format(
            time.strftime('%l:%M%p %Z on %b %d, %Y'))
        sio.emit('info', {'header': 'Train Stopped',
                          'message': message1})
    else:

        if train_movement_started is False:
            train_movement_started = True
            message = 'Movement Started @ {}'.format(
                time.strftime('%l:%M%p %Z on %b %d, %Y'))
            sio.emit('info', {'header': 'Train Started',
                              'message': message})


def proximity(data):
    global train_object_too_close
    # slow things down if an object is in front of sensors.

    how_close = [5, 20, 30, 40]    # how close to object set points
    motor_speeds = [0, 10, 15, 30]  # speeds at how_close set points

    distance = int(data)
    if distance < how_close[0]:
        if debug:
            print("Motor stopped object too close")

        Motor.set_speed(motor_speeds[0])
        # const payload = { header: data.device, message: 'connected' };
        if train_object_too_close is False:
            sio.emit('info', {'header': 'Train warning',
                              'message': 'Train Stopped: Object too close'})
            train_object_too_close = True

    elif distance < how_close[1]:
        if debug:
            print("object less than {}cm".format(how_close[1]))
        if Motor.current_speed > motor_speeds[1]:
            Motor.set_speed(motor_speeds[1])

    elif distance < how_close[2]:
        if debug:
            print("object less than {}cm".format(how_close[2]))
        if Motor.current_speed > motor_speeds[2]:
            Motor.set_speed(motor_speeds[2])

    elif distance < how_close[3]:
        if debug:
            print("object less than {}cm".format(how_close[3]))
        if Motor.current_speed > motor_speeds[3]:
            Motor.set_speed(motor_speeds[3])
    else:
        Motor.set_speed(Motor.current_speed)
        if train_object_too_close:
            sio.emit('info', {'header': 'Train warning',
                              'message': 'Train Restarted: Object Removed'})
            train_object_too_close = False


@sio.on('connect')
def on_connect():
    print('Motor controller: connection established to the main server')
    sio.emit('movement-control', '{"speed":0,"direction":"Forwards"}')


@sio.on('movement-control')
def on_movement_control(data):
    print('sio.on {}'.format(data))
    motor_control(data)


@sio.on('proximity')
def on_proximity(data):
    proximity(data)


@sio.on('ping')  # we have connected. now send data about ourself
def on_con(data):
    # print('our serverId: ', data)
    sio.emit('ping', {'id': data,  'device': 'Motor Service'})


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
    Motor.min_speed = min_speed
    Motor.start()
    print('remote websocket server address: {}' .format(full_url))

    # it just waits for the main server to start.
    # time.sleep(5)
    sio.connect(full_url)
    sio.wait()
    #  anything here won't get executed.!!!
    #  while the program is running.
    destroy()  # probably not needed but it won't do any harm.


except KeyboardInterrupt:
    destroy()
    print('\n\n................... Exit .......................\n\n')
    exit(0)
