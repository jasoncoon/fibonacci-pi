#!/usr/bin/env python3

# Fibonacci256 FancyLED Palettes for CircuitPython
# by Jason Coon, Evil Genius Labs: evilgeniuslabs.org
#
# Based on the Piunora examples: https://github.com/Diodes-Delight/piunora-raspberrypi-os-image/blob/main/scripts/files/piunora-blinka-examples
# and the FancyLED library examples by Phillip Burgess of Adafruit:
# https://learn.adafruit.com/fancyled-library-for-circuitpython/fastled-helpers

import threading

import adafruit_fancyled.fastled_helpers as helper
from rpi_ws281x import Color, PixelStrip

from fibonacci256 import radii
from palettes import palettes, palette_count

# LED strip configuration:
LED_COUNT = 256       # Number of LED pixels.
LED_PIN = 19          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 16   # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53

print('This example needs to be run as root (sudo python3 fancyled-palettes.py)')

# we'll increment this each loop to animate the palettes
hue = 0

# index of the current palette, we'll increment this periodically with a timer
palette_index = 0

# timer used to increment the palette index
timer = None

# current palette
palette = palettes[palette_index]

stopping = False


def next_palette():
    """ Increment the palette index and reset the timer """
    global palette_index
    global palette
    global timer

    # print('next_palette')
    palette_index = (palette_index + 1) % palette_count
    palette = palettes[palette_index]

    if not stopping:
        # reset the timer
        timer = threading.Timer(5.0, next_palette)
        timer.start()


def radius_palette(strip, wait_ms=0):
    """ Fill the LEDs with colors from the current palette based on the LEDs' radii """
    global hue
    global palette

    for i in range(strip.numPixels()):
        radius = radii[i]
        color = helper.ColorFromPalette(palette, radius - hue)
        strip.setPixelColor(i, color.pack())
    strip.show()

    hue = (hue + 1) & 255


def clear(strip):
    """ Turn off all of the LEDs """
    color = Color(0, 0, 0)
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()


# Main program logic follows:
if __name__ == '__main__':
    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

    # Intialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')

    # start the timer used to change palettes periodically
    timer = threading.Timer(5.0, next_palette)
    timer.start()

    try:
        while True:
            radius_palette(strip)

    except KeyboardInterrupt:
        stopping = True
        timer.cancel()
        clear(strip)
