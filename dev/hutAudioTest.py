# Author: Kyler Smith for the Student Design Challenge
# The main execution script for bonbon control, using the Grove Ultrasonic Ranger (which uses the same pin for trigger and receive)
# The sensor's sig pin is connected to the raspberry pi on gpio pin GPIO_SIG (defaults to 6)

# Printing to the console could be removed but is left as a debug / control PC heartbeat signal

# The single Speaker is placed in bonbon"1" or bonbon"2"
speakerIn = 2
# The number of seconds between each audio segment - changed based on emotion
playInterval = 5

import sys
import os

import RPi.GPIO as GPIO
import time

# this package must be from pip package "pyserial"
import serial

from pygame import mixer
from random import randrange
import pathlib

soundsPath = str(pathlib.Path(__file__).parent.resolve()) + "/sounds/"

mixer.init()

bonbon1 = serial.Serial("/dev/rfcomm0")
bonbon2 = serial.Serial("/dev/rfcomm1")

present = False

lastPlay = time.time()

GPIO_SIG = 18

# Checks if the ultrasonic sensor detects an obstacle within range "low" to "high"
def checkRange(low, high):
    global present

    # check distance
    distanceCM = measurementInCM()

    print("Distance : %.1f CM" % distanceCM)

    if distanceCM > low and distanceCM < high and not present:
        print("Person within distance!")
        bonbon1.write(b'h')
        bonbon2.write(b'h')
        present = True
    elif distanceCM < low or distanceCM > high and present:
        print("Person out of distance!")
        bonbon1.write(b'n')
        bonbon2.write(b'n')
        present = False

def measurementInCM():
    # rpi board gpio or bcm gpio
    GPIO.setmode(GPIO.BCM)

    # setup the GPIO_SIG as output
    GPIO.setup(GPIO_SIG, GPIO.OUT)

    GPIO.output(GPIO_SIG, GPIO.LOW)
    time.sleep(0.2)
    GPIO.output(GPIO_SIG, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(GPIO_SIG, GPIO.LOW)
    start = time.time()

    # setup GPIO_SIG as input
    GPIO.setup(GPIO_SIG, GPIO.IN)

    # get duration from Ultrasonic SIG pin
    while GPIO.input(GPIO_SIG) == 0:
        start = time.time()

    while GPIO.input(GPIO_SIG) == 1:
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

def playSound():
    global lastPlay
    global playInterval

    if (time.time() - lastPlay) > playInterval:
        chosenSound = soundsPath

        if present and speakerIn == 2:
            chosenSound += "anxious"
            playInterval = 5
        elif not present and speakerIn == 1:
            chosenSound += "sad"
            playInterval = 25
        elif (present and speakerIn == 1) or (not present and speakerIn == 2):
            chosenSound += "happy"
            playInterval = 15

        chosenSound += str(randrange(3) + 1) + ".wav"

        sound = mixer.Sound(chosenSound)

        sound.play()

        lastPlay = time.time()

def main():
    while True:
        checkRange(0, 100)
        playSound()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Keyboard Interrupt! GPIO Cleaned Up\n")
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)