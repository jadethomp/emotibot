#!/usr/bin/python3.9

# ran dos2unix...

# Authors: Kyler Smith for the Student Design Challenge
# The main execution script for bonbon control, using an adaption of the Grove Ultrasonic Ranger

# Printing to the console could be removed but is left as a debug / control PC heartbeat signal

import sys
import os
from pasimple import play_wav
import pathlib

import RPi.GPIO as GPIO
import time
import random

# this package must be from pip package "pyserial"
import serial
bonbon1BT = serial.Serial("/dev/rfcomm0")
bonbon2BT = serial.Serial("/dev/rfcomm1")

lastTransmit = time.time()
nextSound1 = time.time()
nextSound2 = time.time()

soundsPath = str(pathlib.Path(__file__).parent.resolve()) + "/sounds/"
happySounds = ["Lhappy1.wav", "Lhappy2.wav", "Lhappy3.wav", "Rhappy1.wav", "Rhappy2.wav", "Rhappy3.wav"]
sadSounds = ["Lsad1.wav", "Lsad2.wav", "Lsad3.wav"]
anxiousSounds = ["Ranxious1.wav", "Ranxious2.wav", "Ranxious3.wav"]

local_userPresent = False

bonbon1State = False
bonbon2State = False

# The signal pin of the ultrasonic sensor
# Labeled as the Raspberry pi's numerical GPIO pin
GPIO_TRIG = 17
GPIO_ECHO = 27

def checkState(which):
    global bonbon1State
    global bonbon2State
    if(which == 1):
        if(bonbon1BT.in_waiting > 0):
            newvalue = bonbon1BT.read(1)
            if(newvalue == b'h'):
                bonbon1State = True
                print("BonBon1 says here")
            elif(newvalue == b'n'):
                bonbon1State = False
                print("BonBon1 says not here")
            print(newvalue)
    elif(which == 2):
        if(bonbon2BT.in_waiting > 0):
            newvalue = bonbon2BT.read(1)
            if(newvalue == b'h'):
                bonbon2State = True
                print("BonBon2 says here")
            elif(newvalue == b'n'):
                bonbon2State = False
                print("BonBon2 says not here")

def playSound(which):
    global bonbon1State
    global bonbon2State
    global nextSound1
    global nextSound2
    if(which == 1):
        if(time.time() >= nextSound1):
            print("Playing Sound on bonbon1")
            if(bonbon1State == True):
                # play random happy
                play_wav(soundsPath + str(happySounds[random.randrange(0, 2)]))
            elif(bonbon1State == False):
                # play random sad
                play_wav(soundsPath + str(sadSounds[random.randrange(0, 2)]))
            # reset next sound
            nextSound1 = time.time() + random.randrange(6, 12)
    elif(which == 2):
        if(time.time() >= nextSound2):
            print("Playing Sound on bonbon2")
            if(bonbon2State == True):
                # play random anxious
                play_wav(soundsPath + str(anxiousSounds[random.randrange(0, 2)]))
                # reset next sound
                nextSound2 = time.time() + random.randrange(3, 5)
            elif(bonbon2State == False):
                # play random happy
                play_wav(soundsPath + str(happySounds[random.randrange(3, 5)]))
                # reset next sound
                nextSound2 = time.time() + random.randrange(6, 12)


# Checks if the ultrasonic sensor detects an obstacle within range "low" to "high"
def checkRange(low, high):
    global local_userPresent
    global lastTransmit
    # print("BonBon Detecting Distance")

    shouldSend = False
    sendVal = b'h'

    # check distance
    distanceCM = measurementInCM()

    # print("Distance : %.1f CM" % distanceCM)

    if distanceCM > low and distanceCM < high and not local_userPresent:
        print("Person within distance!")
        # bonbon1BT.write(b'h')
        # bonbon2BT.write(b'h')
        sendVal = b'h'
        shouldSend = True
        local_userPresent = True
    elif distanceCM < low or distanceCM > high and local_userPresent:
        print("Person out of distance!")
        # bonbon1BT.write(b'n')
        # bonbon2BT.write(b'n')
        sendVal = b'n'
        shouldSend = True
        local_userPresent = False

    # Enforce an interval
    now = time.time()
    transmitInterval = now - lastTransmit
    if transmitInterval > 3:
        if shouldSend:
            print("Transmitting")
            bonbon1BT.write(sendVal)
            bonbon2BT.write(sendVal)
            shouldSend = False
            lastTransmit = now

def measurementInCM():
    # pulse to trigger the module, to start the ranging program
    GPIO.output(GPIO_TRIG, True)
    time.sleep(0.0001)
    GPIO.output(GPIO_TRIG, False)

    # get duration from Ultrasonic SIG pin
    while GPIO.input(GPIO_ECHO) == 0:
        start = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        stop = time.time()

    return calcDistance(start, stop)


def calcDistance(start, stop):
    # Calculate pulse length
    elapsed = stop-start

    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s)
    distance = elapsed * 34300

    # That was the distance there and back so halve the value
    distance = distance / 2

    return distance

def main():
    global nextSound1
    global nextSound2
    # rpi board gpio or bcm gpio
    GPIO.setmode(GPIO.BCM)

    # setup the GPIO_SIG as output
    GPIO.setup(GPIO_TRIG, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

    GPIO.output(GPIO_TRIG, False)

    # waiting for sensor to settle
    time.sleep(2)

    nextSound1 = time.time() + random.randrange(7, 21)
    nextSound2 = time.time() + random.randrange(7, 21)
    while True:
        time.sleep(0.5)
        checkRange(0, 100)
        checkState(1)
        checkState(2)
        playSound(1)
        playSound(2)

if __name__ == '__main__':
    try:
        print("Begin Student Design Challenge Loop")
        print("Press CTRL+C to stop")
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Keyboard Interrupt! GPIO Cleaned Up\n")
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)