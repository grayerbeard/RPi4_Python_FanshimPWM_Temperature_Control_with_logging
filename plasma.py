"""Library for the Pimoroni Blinkt! - 8-pixel APA102 LED display."""

# assed in case code being used on a system where this has not been installed

import atexit
import time

import RPi.GPIO as GPIO


__version__ = '0.0.1'

DAT = 15
CLK = 14
PIXELS_PER_LIGHT = 4
DEFAULT_BRIGHTNESS = 3
MAX_BRIGHTNESS = 3
NUM_PIXELS = 0


pixels = []

_light_count = 0
_gpio_setup = False
_clear_on_exit = False


def _exit():
    if _clear_on_exit:
        clear()
        show()
    GPIO.cleanup()


def use_pins(data, clock):
    """Set alternate data and clock pins for your Plasma chain."""
    global DAT, CLK, _gpio_setup
    if DAT != data or CLK != clock:
        _gpio_setup = False
    DAT = data
    CLK = clock


def set_light_count(light_count):
    """Set the number of light modules in your Plasma chain."""
    global _light_count, pixels, NUM_PIXELS
    _light_count = light_count
    NUM_PIXELS = light_count * PIXELS_PER_LIGHT
    pixels = [[0, 0, 0, DEFAULT_BRIGHTNESS]] * light_count * PIXELS_PER_LIGHT


def set_light(index, r, g, b):
    """Set the RGB colour of an individual light in your Plasma chain.

    This will set all four LEDs on the Plasma light to the same colour.

    :param index: Index of the light in your chain (starting at 0)
    :param r: Amount of red: 0 to 255
    :param g: Amount of green: 0 to 255
    :param b: Amount of blue: 0 to 255

    """
    offset = index * 4
    for x in range(4):
        set_pixel(offset + x, r, g, b)


def set_brightness(brightness):
    """Set the brightness of all pixels.

    :param brightness: Brightness: 0.0 to 1.0

    """
    if brightness < 0 or brightness > 1:
        raise ValueError('Brightness should be between 0.0 and 1.0')

    for x in range(_light_count * PIXELS_PER_LIGHT):
        pixels[x][3] = int(float(MAX_BRIGHTNESS) * brightness) & 0b11111


def clear():
    """Clear the pixel buffer."""
    for x in range(_light_count * PIXELS_PER_LIGHT):
        pixels[x][0:3] = [0, 0, 0]


def _write_byte(byte):
    for x in range(8):
        GPIO.output(DAT, byte & 0b10000000)
        GPIO.output(CLK, 1)
        time.sleep(0.0000005)
        byte <<= 1
        GPIO.output(CLK, 0)
        time.sleep(0.0000005)


# Emit exactly enough clock pulses to latch the small dark die APA102s which are weird
# for some reason it takes 36 clocks, the other IC takes just 4 (number of pixels/2)
def _eof():
    GPIO.output(DAT, 0)
    for x in range(36):
        GPIO.output(CLK, 1)
        time.sleep(0.0000005)
        GPIO.output(CLK, 0)
        time.sleep(0.0000005)


def _sof():
    GPIO.output(DAT, 0)
    for x in range(32):
        GPIO.output(CLK, 1)
        time.sleep(0.0000005)
        GPIO.output(CLK, 0)
        time.sleep(0.0000005)


def show():
    """Output the buffer to Blinkt!."""
    global _gpio_setup

    if not _gpio_setup:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(DAT, GPIO.OUT)
        GPIO.setup(CLK, GPIO.OUT)
        atexit.register(_exit)
        _gpio_setup = True

    _sof()

    for pixel in pixels:
        r, g, b, brightness = pixel
        _write_byte(0b11100000 | brightness)
        _write_byte(b)
        _write_byte(g)
        _write_byte(r)

    _eof()


def set_all(r, g, b, brightness=None):
    """Set the RGB value and optionally brightness of all pixels.

    If you don't supply a brightness value, the last value set for each pixel be kept.

    :param r: Amount of red: 0 to 255
    :param g: Amount of green: 0 to 255
    :param b: Amount of blue: 0 to 255
    :param brightness: Brightness: 0.0 to 1.0 (default is 1.0)

    """
    for x in range(_light_count * PIXELS_PER_LIGHT):
        set_pixel(x, r, g, b, brightness)


def get_pixel(x):
    """Get the RGB and brightness value of a specific pixel.

    :param x: The horizontal position of the pixel: 0 to 7

    """
    r, g, b, brightness = pixels[x]
    brightness /= float(MAX_BRIGHTNESS)

    return r, g, b, round(brightness, 3)


def set_pixel(x, r, g, b, brightness=None):
    """Set the RGB value, and optionally brightness, of a single pixel.

    If you don't supply a brightness value, the last value will be kept.

    :param x: The horizontal position of the pixel: 0 to 7
    :param r: Amount of red: 0 to 255
    :param g: Amount of green: 0 to 255
    :param b: Amount of blue: 0 to 255
    :param brightness: Brightness: 0.0 to 1.0 (default around 0.2)

    """
    if brightness is None:
        brightness = pixels[x][3]
    else:
        brightness = int(float(MAX_BRIGHTNESS) * brightness) & 0b11111

    pixels[x] = [int(r) & 0xff, int(g) & 0xff, int(b) & 0xff, brightness]


def set_clear_on_exit(value=True):
    """Set whether Plasma Lights should be cleared upon exit.

    By default Plasma will not turn off the pixels on exit, but calling::

        plasma.set_clear_on_exit(True)

    Will ensure that it does.

    :param value: True or False (default True)

    """
    global _clear_on_exit
    _clear_on_exit = value
