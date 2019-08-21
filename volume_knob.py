#!/usr/bin/env python

import configparser
from time import sleep

from pythonosc.udp_client import SimpleUDPClient
from powermate import find_wheels
from powermate import PowerMateWheel

volume = .75

def set_volume():
    global volume
    if (volume < 0.0):
        volume = 0
    elif (volume > 1.0):
        volume = 1.0
        pass
    client.send(BOARD_CHANNEL, volume)

    my_wheel.brightness(int(volume * 255))
    print("setting volume to {}".format(volume))

def read_config():
    try:
        config = configparser.ConfigParser()
        config.read('/home/pi/volume_knob.cfg')

        BOARD_ADDRESS = config.get('BOARD', 'address')
        BOARD_CHANNEL = config.get('BOARD', 'channel')
        BOARD_PORT = 10023
        try:
            BOARD_PORT = int(config.get('BOARD', 'port'))
        except:
            pass

        BOARD_DEFAULT_VOLUME = .75
        try:
            BOARD_DEFAULT_VOLUME = float(config.get('BOARD', 'default_volume'))
        except:
            pass

        volume = BOARD_DEFAULT_VOLUME
        
        WHEEL_SPEED = .01
        try:
            WHEEL_SPEED = float(config.get('WHEEL', 'speed'))
        except:
            pass
    except:
        return "", "", "", ""    
    return BOARD_ADDRESS, BOARD_CHANNEL, BOARD_PORT, WHEEL_SPEED

device = find_wheels()
print("found wheels: {}".format(device))

my_wheel = PowerMateWheel(device[0])

def error_throb(count):
    for current_pass in range(count):
        for i in range(255):
            my_wheel.brightness(i)
            sleep(.01)
        for i in range(255):
            my_wheel.brightness(255-i)
            sleep(.01)
            pass
        pass
    pass


BOARD_ADDRESS, BOARD_CHANNEL, BOARD_PORT, WHEEL_SPEED = read_config()

while (not BOARD_ADDRESS or not BOARD_CHANNEL or not BOARD_PORT or not WHEEL_SPEED):
    error_throb(3)
    BOARD_ADDRESS, BOARD_CHANNEL, BOARD_PORT, WHEEL_SPEED = read_config()
    sleep(5)


print("Connecting to Sound Board...")
client = SimpleUDPClient(BOARD_ADDRESS, BOARD_PORT)
print("Connected.")
print("setting volume")
set_volume()

def change_volume(direction):
    def vol(*args):
        global volume
        if (direction=="left"):
            volume -= .01
        else:
            volume += .01
        print("chg volume {}".format(volume))
        set_volume()
    return vol

my_wheel.on('turn_left', change_volume('left'))
my_wheel.on('turn_right', change_volume('right'))
print("initializing listener")
try:
    my_wheel.listen()
except:
    print("Stopping Volume Knob...")
    pass
