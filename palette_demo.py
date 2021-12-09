#!/usr/bin/env python3

# Fibonacci256 FancyLED Palettes Demo
# by Jason Coon, Evil Genius Labs: evilgeniuslabs.org
#
# Based on the Piunora examples: https://github.com/Diodes-Delight/piunora-raspberrypi-os-image/blob/main/scripts/files/piunora-blinka-examples
# and the FancyLED library examples by Phillip Burgess of Adafruit:
# https://learn.adafruit.com/fancyled-library-for-circuitpython/fastled-helpers

import time

import adafruit_fancyled.adafruit_fancyled as fancy
import adafruit_fancyled.fastled_helpers as helper
from rpi_ws281x import Color, PixelStrip

from fibonacci256_maps import radii
from palettes import palette_count, palettes

# LED strip configuration:
LED_COUNT = 256       # Number of LED pixels.
LED_PIN = 19          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 32   # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53

print('This example needs to be run as root (sudo python3 fancyled-palettes.py)')

# we'll increment this each loop to animate the palettes
hue = 0

# index of the current palette, we'll increment this periodically with a timer
palette_index = 0

# timer used to increment the palette index
next_palette_time = time.monotonic() + 5

# timer used to blend the current palette to the next
blend_palette_time = time.monotonic() + 0.04

current_palette = palettes[palette_index].copy()
target_palette = palettes[palette_index]


def next_palette():
    """ Increment the palette index and reset the timer """
    global palette_index
    global target_palette
    global next_palette_time

    # print('next_palette')
    palette_index = (palette_index + 1) % palette_count
    target_palette = palettes[palette_index]

    next_palette_time = time.monotonic() + 5


def blend_palettes(current, target, weight):
    for i in range(len(current)):
        current[i] = fancy.mix(current[i], target[i], weight)


def blend_current_palette():
    """ Blend the palettes and reset the timer """
    global palette_index
    global target_palette
    global current_palette
    global blend_palette_time

    # print('blend_palettes')
    blend_palettes(current_palette, target_palette, 0.01)

    blend_palette_time = time.monotonic() + 0.04


def radius_palette(strip, wait_ms=0):
    """ Fill the LEDs with colors from the current palette based on the LEDs' radii """
    global hue
    global target_palette

    for i in range(strip.numPixels()):
        radius = radii[i]
        color = helper.ColorFromPalette(current_palette, radius - hue)
        strip.setPixelColor(i, color.pack())
    strip.show()


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

    try:
        while True:
            radius_palette(strip)

            hue = (hue + 1) & 255

            if time.monotonic() > next_palette_time:
                next_palette()

            if time.monotonic() > blend_palette_time:
                blend_current_palette()

    except KeyboardInterrupt:
        clear(strip)
