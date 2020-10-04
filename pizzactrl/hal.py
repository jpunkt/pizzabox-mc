import logging
import functools
from time import sleep

from typing import Any, List
from scipy.io.wavfile import write as writewav

import sounddevice as sd
import soundfile as sf
import numpy as np

from . import gpio_pins

from picamera import PiCamera
from gpiozero import Button, OutputDevice, PWMOutputDevice, PWMLED


logger = logging.getLogger(__name__)


# Constants
VIDEO_RES = (1920, 1080)  # Video Resolution
PHOTO_RES = (2592, 1944)  # Photo Resolution
AUDIO_REC_SR = 44100      # Audio Recording Samplerate


class Motor:
    def __init__(self, in1, in2, enable):
        self._in1 = OutputDevice(in1)
        self._in2 = OutputDevice(in2)
        self._en = PWMOutputDevice(enable)

    @property
    def direction(self):
        return self._in1.value > self._in2.value

    @direction.setter
    def direction(self, cw=True):
        if cw is None:
            self._in1.value = self._in2.value = 0
        if cw:
            self._in1.value = 1
            self._in2.value = 0
        else:
            self._in1.value = 0
            self._in2.value = 1

    @property
    def speed(self):
        return self._en.value * (1.0 if self.direction else -1.0)

    @speed.setter
    def speed(self, speed: float):
        """
        Turn on motor. Negative speed = CCW direction

        :param speed: float [-1.0 .. 1.0]
        """
        if self.speed == speed:
            return

        if speed == 0:
            self.off()
            return

        if abs(speed) > 1.:
            speed = 1. if speed > 0 else -1.

        self.direction = speed > 0
        self._en.value = abs(speed)

    def off(self):
        """
        Stop motor
        """
        if self._en.is_active:
            self._en.off()
            self.direction = None


class ScrollSensor:
    def __init__(self, low_bit: int, high_bit: int, endstop: int):
        self._low = Button(low_bit, pull_up=False)
        self._high = Button(high_bit, pull_up=False)
        self._end = Button(endstop, pull_up=False)

        # self._low.when_released = self._callback

        # self.direction = 0
        # self.count = 0

    # def _callback(self):
    #     logger.debug(f'callback(), low_bit={self._low.value}, '
    #                  f'high_bit={self._high.value}, count={self.count}')
    #     if self._high.is_pressed is self._low.is_pressed:
    #         self.direction = -1
    #     else:
    #         self.direction = 1
    #     self.count += self.direction

    # def wait_for_tick(self):
    #     """
    #     do nothing until flank on sensor inputs
    #     """
    #     _count = self.count
    #     while self.count == _count:
    #         pass

    @property
    def eot_callback(self):
        return self._low.when_pressed

    @eot_callback.setter
    def eot_callback(self, callback):
        self._high.when_pressed = callback

    @property
    def stop_callback(self):
        return self._end.when_pressed

    @stop_callback.setter
    def stop_callback(self, callback):
        self._end.when_pressed = callback


class PizzaHAL:
    """
    This class holds a represenation of the pizza box hardware and provides
    methods to interact with it.

    - lights upper/lower on/off
    - motor up-down/left-right speed distance
    - scroll up-down/left-right positions
    - lid open/closed detectors
    - user interface buttons

    """

    def __init__(self):
        self.btn_forward = Button(gpio_pins.BTN_FORWARD_GPIO)
        self.btn_back = Button(gpio_pins.BTN_BACK_GPIO)

        self.led_btn_fwd = PWMLED(gpio_pins.LED_FWD_BTN)
        self.led_btn_back = PWMLED(gpio_pins.LED_BACK_BTN)

        # self.lid_sensor = Button(gpio_pins.LID_SWITCH)

        self.ud_sensor = ScrollSensor(*gpio_pins.SCROLL_UPDOWN_SENSORS,
                                      gpio_pins.SCROLL_UPDOWN_ENDSTOP)
        self.lr_sensor = ScrollSensor(*gpio_pins.SCROLL_LR_SENSORS,
                                      gpio_pins.SCROLL_LR_ENDSTOP)

        self.motor_lr = Motor(*gpio_pins.MOTOR_CTRL_LR)
        self.motor_ud = Motor(*gpio_pins.MOTOR_CTRL_UPDOWN)
        self.led_layer = PWMOutputDevice(gpio_pins.LED_LAYER)
        self.led_backlight = PWMOutputDevice(gpio_pins.LED_BACKLIGHT)

        self.camera = None
        self.soundcache = {}

        self.blocked = False


def blocking(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        hal = kwargs.get('hal', None)
        if hal is not None:
            while hal.blocked:
                pass
            hal.blocked = True
        func(*args, **kwargs)
        if hal is not None:
            hal.blocked = False
    return _wrapper


def _move(motor: Motor, sensor: ScrollSensor, speed: float = 1.0,
          distance: int = 0, ramp=True):
    """
    Expecting speed to be always positive, but distance to show direction

    :param motor:
    :param sensor:
    :param speed:
    :param distance:
    :param ramp:
    :return:
    """
    try:
        motor.off()
        sensor.count = 0
        # acceleration parameters
        acc_dist = 0
        increment = 0
        speed = abs(speed)
        # set direction
        if distance < 0:
            speed = -abs(speed)

        # only accelerate on longer distances
        if ramp and distance > 20:
            # calculate speed increment per tick
            acc_dist = int(distance * 0.1)
            increment = speed / acc_dist

        logger.debug(f'distance={distance}')
        while abs(sensor.count) < abs(distance):
            if abs(sensor.count) < abs(acc_dist):     # accelerate
                motor.speed += increment
            elif abs(sensor.count) > abs(distance - acc_dist):  # decelerate
                motor.speed -= increment
            else:                           # set speed and wait
                motor.speed = speed
            sensor.wait_for_tick()
    finally:
        motor.off()


@blocking
def advance(motor: Motor, sensor: ScrollSensor, speed: float,
            direction: bool=True):
    """
    Move the motor controlling the up-down scroll a given distance at a
    given speed.

    """
    sensor.stop_callback = motor.off
    sensor.eot_callback = motor.off
    motor.speed = speed if direction else -speed
    # Safety catch
    sleep(1.5)
    motor.off()
    sensor.stop_callback = None
    sensor.eot_callback = None


@blocking
def rewind(motor: Motor, sensor: ScrollSensor, direction: bool=True,
           max_time: float=13.2):
    sensor.eot_callback = motor.off
    sensor.stop_callback = None
    motor.speed = -0.3 if direction else 0.3
    # Safety catch
    sleep(max_time)
    motor.off()


def turn_off(hal: PizzaHAL):
    """
    Rewind the scrolls to starting position

    :param hal: The hardware abstraction object
    """
    hal.led_btn_back.off()
    hal.led_btn_fwd.off()
    hal.led_layer.off()
    hal.led_backlight.off()
    hal.btn_back.when_pressed = None
    hal.btn_back.when_held = None
    hal.btn_forward.when_pressed = None
    hal.btn_forward.when_held = None
    hal.motor_ud.off()
    hal.motor_lr.off()


def wait_for_input(hal: PizzaHAL, go_callback, back_callback, **kwargs):
    """
    Blink leds on buttons. Wait until the user presses a button, then execute
    the appropriate callback

    :param hal: The hardware abstraction object
    :param go_callback: called when button 'go' is pressed
    :param back_callback: called whan button 'back' is pressed
    """
    hal.led_btn_fwd.blink(0.3, 0.3, 0.15, 0.15)
    hal.led_btn_back.blink(0.3, 0.3, 0.15, 0.15)

    hal.blocked = True

    hal.btn_forward.when_pressed = \
        _wrap_wait_btn(hal, go_callback, **kwargs)

    hal.btn_back.when_pressed = \
        _wrap_wait_btn(hal, back_callback, **kwargs)

    # Wait until button is pressed. is_pressed output is inverted
    while hal.blocked:
        pass

    sleep(0.5)


def _wrap_wait_btn(hal, callback, **kwargs):
    @functools.wraps(callback)
    def wrapper():
        hal.blocked = True
        if callback is not None:
            callback(hal=hal, **kwargs)
        hal.btn_forward.when_pressed = None
        hal.btn_back.when_pressed = None
        hal.led_btn_back.off()
        hal.led_btn_fwd.off()
        hal.blocked = False
    return wrapper


def _fade_led(led_pin: PWMOutputDevice, intensity: float, fade: float = 1.0,
              steps: int = 100):
    brightness = led_pin.value
    step = (intensity - brightness) / float(steps)
    wait = fade / float(steps)

    if step != 0.:
        for i in np.arange(brightness, intensity, step):
            led_pin.value = i
            sleep(wait)

    led_pin.value = intensity


@blocking
def light_layer(hal: PizzaHAL, intensity: float, fade: float = 0.0,
                steps: int = 100, **kwargs):
    """
    Turn on the light to illuminate the upper scroll

    :param hal: The hardware abstraction object
    :param fade: float
                Default 0, time in seconds to fade in or out
    :param intensity: float
                Intensity of the light in percent
    :param steps: int
                How many steps for the fade (default: 10)
    """
    if fade > 0.:
        _fade_led(hal.led_layer, intensity, fade, steps)
    else:
        hal.led_layer.value = intensity


@blocking
def backlight(hal: PizzaHAL, intensity: float, fade: float = 0.0,
              steps: int = 100, **kwargs):
    """
    Turn on the backlight

    :param hal: The hardware abstraction object
    :param fade: float
                Default 0, time in seconds to fade in or out
    :param intensity: float
                Intensity of the light in percent
    :param steps: int
                How many steps for the fade (default: 10)
    """
    if fade > 0.:
        _fade_led(hal.led_backlight, intensity, fade, steps)
    else:
        hal.led_backlight.value = intensity


@blocking
def play_sound(hal: PizzaHAL, sound: Any, **kwargs):
    """
    Play a sound.

    :param hal: The hardware abstraction object
    :param sound: The sound to be played
    """
    # Extract data and sampling rate from file
    try:
        data, fs = hal.soundcache.get(str(sound), sf.read(str(sound), dtype='float32'))
        sd.play(data, fs)
        sd.wait()  # Wait until file is done playing
    except KeyboardInterrupt:
        logger.debug('skipped playback')
        # sd.stop()


@blocking
def record_sound(hal: PizzaHAL, filename: Any, duration: int,
                 cache: bool = False, **kwargs):
    """
    Record sound using the microphone

    :param hal: The hardware abstraction object
    :param filename: The path of the file to record to
    :param duration: The time to record in seconds
    :param cache: `True` to save recording to cache. Default is `False`
    """
    myrecording = sd.rec(int(duration * AUDIO_REC_SR),
                         samplerate=AUDIO_REC_SR,
                         channels=2)
    sd.wait()  # Wait until recording is finished
    writewav(str(filename), AUDIO_REC_SR, myrecording)
    if cache:
        hal.soundcache[str(filename)] = (myrecording, AUDIO_REC_SR)


@blocking
def record_video(hal: PizzaHAL, filename: Any, duration: float, **kwargs):
    """
    Record video using the camera

    :param hal: The hardware abstraction object
    :param filename: The path of the file to record to
    :param duration: The time to record in seconds
    """
    hal.camera.resolution = VIDEO_RES
    hal.camera.start_recording(str(filename))
    hal.camera.wait_recording(duration)
    hal.camera.stop_recording()


@blocking
def take_photo(hal: PizzaHAL, filename: Any, **kwargs):
    """
    Take a foto with the camera

    :param hal: The hardware abstraction object
    :param filename: The path of the filename for the foto
    """
    hal.camera.resolution = PHOTO_RES
    hal.camera.capture(str(filename))


@blocking
def init_sounds(hal: PizzaHAL, sounds: List):
    """
    Load prerecorded Sounds into memory

    :param hal:
    :param sounds: A list of sound files
    """
    if hal.soundcache is None:
        hal.soundcache = {}

    for sound in sounds:
        # Extract data and sampling rate from file
        data, fs = sf.read(str(sound), dtype='float32')
        hal.soundcache[str(sound)] = (data, fs)


@blocking
def init_camera(hal: PizzaHAL):
    if hal.camera is None:
        hal.camera = PiCamera()
