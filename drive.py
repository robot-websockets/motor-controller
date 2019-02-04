
# !/usr/bin/python3
#
# Python Module to externalise Picocon Motor Driver hardware
#
# Created by Gareth Davies, Sep 2013
# Copyright 4tronix
#
# This code is in the public domain and may be freely copied and used
# No warranty is provided or implied
#
# ======================================================================


# ======================================================================
# General Functions
#
# init(). Initialises GPIO pins, switches motors off, etc
# cleanup(). Sets all motors off and sets GPIO to standard values

# Import all necessary libraries
import RPi.GPIO as GPIO
# , sys, threading, time, os

# Pins 24, 26 Right Motor
# Pins 19, 21 Left Motor
L1 = 21
L2 = 19
R1 = 26
R2 = 24

# ======================================================================
# General Functions
#
# init(). Initialises GPIO pins, switches motors and LEDs Off, etc


def init():

    global p, q, a, b

    GPIO.setwarnings(False)

    # use physical pin numbering
    GPIO.setmode(GPIO.BOARD)

    # use pwm on motor outputs so motors can be controlled
    GPIO.setup(L1, GPIO.OUT)
    p = GPIO.PWM(L1, 20)
    p.start(0)

    GPIO.setup(L2, GPIO.OUT)
    q = GPIO.PWM(L2, 20)
    q.start(0)

    GPIO.setup(R1, GPIO.OUT)
    a = GPIO.PWM(R1, 20)
    a.start(0)

    GPIO.setup(R2, GPIO.OUT)
    b = GPIO.PWM(R2, 20)
    b.start(0)

# cleanup(). Sets all motors off and sets GPIO to standard values


def cleanup():

    stop()
    GPIO.cleanup()

# End of General Functions
# ======================================================================


# ======================================================================
# Motor Functions
#
# stop(): Stops both motors


def stop():

    p.ChangeDutyCycle(0)
    q.ChangeDutyCycle(0)
    a.ChangeDutyCycle(0)
    b.ChangeDutyCycle(0)

# forward(speed): Sets both motors to move forward at speed. 0 <= speed <= 100


def forward(speed):

    p.ChangeDutyCycle(0)
    q.ChangeDutyCycle(speed)
    a.ChangeDutyCycle(0)
    b.ChangeDutyCycle(speed)
    q.ChangeFrequency(speed + 5)
    b.ChangeFrequency(speed + 5)

# reverse(speed): Sets both motors to reverse at speed. 0 <= speed <= 100


def reverse(speed):

    p.ChangeDutyCycle(speed)
    q.ChangeDutyCycle(0)
    a.ChangeDutyCycle(speed)
    b.ChangeDutyCycle(0)
    p.ChangeFrequency(speed + 5)
    a.ChangeFrequency(speed + 5)


# End of Motor Functions
# ======================================================================

# ======================================================================
# __main__ Code
# ======================================================================

if __name__ == "__main__":
    print("\n\nThis file cannot be run directly. It is intended to be imported\n\n")
else:
    print("\n\nImporting drive.py")

# End of __main__ Code
# ======================================================================
