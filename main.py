import sys
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
        # Turn off motors.

    def start_running(self):
        self.running = True

    def ramp_speed(self, interval):
        self.ramp_speed = interval

    def set_message(self, message):
        self.message = message

    def set_speed(self, speed):
        self.requested_speed = speed
        print("speed is now: {}".format(speed))

    def set_direction(self, direction):
        self.direction = direction
        print("direction is now: {}".format(direction))


def motor_control(jsondata):

    # print(jsondata)
    data = json.loads(jsondata)
    # print('dir: {}  speed: {}'.format(data['direction'], data['speed']))

    Motor.set_speed(int(data['speed']))
    Motor.set_direction(data['direction'])


@sio.on('connect')
def on_connect():
    print('Motor controller: connection established to the main server')


@sio.on('movement-control')
def on_movement_control(data):
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


if args.ws_server:
    # create a new  MotorController to use
    Motor = MotorController()
    Motor.start()
    web_socket_server = args.ws_server
    print('remote websocket server address: http://{}:5001:'
          .format(web_socket_server))

    # this can be removed if no in docker
    # it just waits for the main server to start.
    time.sleep(5)
    sio.connect('http://{}:5001'.format(web_socket_server))
    sio.wait()
    #  anything here won't get executed.!!!
else:
    print('No -ws_server or -W entered.\nYou need to enter a' +
          'serveraddress:\n\n try:> python main.py -W "192.168.0.18"\n')
    sys.exit()
