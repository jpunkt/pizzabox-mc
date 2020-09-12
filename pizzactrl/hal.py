from time import sleep

from typing import Any

from . import gpio_pins

from picamera import PiCamera
from gpiozero import Button, OutputDevice, PWMOutputDevice, PWMLED


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
        return self._en.value * 1.0 if self.direction else -1.0

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

        self.direction = (speed > 0)
        self._en.value = abs(speed)

    def off(self):
        """
        Stop motor
        """
        if self._en.is_active:
            self._en.off()
            self._set_direction(None)


class ScrollSensor:
    def __init__(self, low_bit, high_bit):
        self._low = Button(low_bit)
        self._high = Button(high_bit)
        self._low.when_pressed = self._high_callback
        self._low.when_released = self._low_callback

        self._direction = 0
        self._count = 0

    def _high_callback(self):
        # TODO implement
        pass

    def _low_callback(self):
        # TODO implement
        pass

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, count):
        self._count = count

    @property
    def direction(self):
        return self._direction

    def wait_for_tick(self):
        """
        do nothing until flank on sensor inputs
        """
        _count = self.count
        while self.count == _count:
            pass


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

        self.lid_sensor = Button(gpio_pins.LID_SWITCH)

        self.ud_endstop = Button(gpio_pins.SCROLL_UPDOWN_ENDSTOP)
        self.lr_endstop = Button(gpio_pins.SCROLL_LR_ENDSTOP)
        self.ud_sensor = ScrollSensor(*gpio_pins.SCROLL_UPDOWN_SENSORS)
        self.lr_sensor = ScrollSensor(*gpio_pins.SCROLL_LR_SENSORS)

        # self.camera = PiCamera()  # TODO enable
        self.motor_lr = Motor(*gpio_pins.MOTOR_CTRL_LR)
        self.motor_ud = Motor(*gpio_pins.MOTOR_CTRL_UPDOWN)
        self.led_layer = PWMOutputDevice(gpio_pins.LED_LAYER)
        self.led_backlight = PWMOutputDevice(gpio_pins.LED_BACKLIGHT)


def _move(motor: Motor, sensor: ScrollSensor, speed: float = 1.0,
          distance: int = 0, ramp = True):
    motor.off()
    sensor.count = 0
    # acceleration parameters
    acc_dist = 0
    increment = 0
    # only accelerate on longer distances
    if ramp and distance > 10:
        # calculate speed increment per tick
        acc_dist = int(distance * 0.1)
        increment = speed / acc_dist

    while sensor.count < distance:
        if sensor.count < acc_dist:     # accelerate
            motor.speed += increment
        elif sensor.count > (distance - acc_dist):  # decelerate
            motor.speed -= increment
        else:                           # set speed and wait
            motor.speed = speed
        sensor.wait_for_tick()

    motor.off()


def move_updown(hal: PizzaHAL, speed: float, distance: int):
    """
    Move the motor controlling the up-down scroll a given distance at a
    given speed.

    :param hal: The hardware abstraction object
    :param speed: float [-1.0 .. 1.0]
                    speed factor for motor
    :param distance: positive int
                    distance to travel in tics
    """
    _move(hal.motor_ud, hal.ud_sensor, speed, distance)


def move_leftright(hal: PizzaHAL, speed: float, distance: int):
    """
    Move the motor controlling the left-right scroll a given distance at a
    given speed.

    :param hal: The hardware abstraction object
    :param speed: float [-1.0 .. 1.0]
                    speed factor for motor
    :param distance: positive int
                    distance to travel in tics
    """
    _move(hal.motor_lr, hal.ud_sensor, speed, distance)


def rewind(hal: PizzaHAL):
    """
    Rewind the scrolls to starting position

    :param hal: The hardware abstraction object
    """
    pass


def wait_for_input(hal: PizzaHAL, go_callback, back_callback, **kwargs):
    """
    Blink leds on buttons. Wait until the user presses a button, then execute
    the appropriate callback

    :param hal: The hardware abstraction object
    :param go_callback: called when button 'go' is pressed
    :param back_callback: called whan button 'back' is pressed
    :param kwargs: parameters passed to back_callback
    """
    pass


def _fade_led(led_pin: PWMOutputDevice, intensity: float, fade = 1.0,
              steps: int = 10):
    brightness = led_pin.value
    step = (intensity - brightness) / float(steps)
    wait = fade / float(steps)

    while brightness < intensity:
        brightness += step
        led_pin.value = brightness
        sleep(wait)

    led_pin.value = intensity


def light_layer(hal: PizzaHAL, intensity: float, fade: float = 0.0,
                steps: int = 10):
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


def backlight(hal: PizzaHAL, intensity: float, fade: float = 0.0,
                steps: int = 10):
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


def play_sound(hal: PizzaHAL, sound: Any, block: bool):
    """
    Play a sound.

    :param hal: The hardware abstraction object
    :param sound: The sound to be played
    :param block: When `True` do not allow other actions while playing
    """
    pass


def play_sound_insert(hal: PizzaHAL, *args):
    """
    Play multiple sounds in succession

    :param hal: The hardware abstraction object
    :param args: a list of sound files
    """
    pass


def record_sound(hal: PizzaHAL, filename: str, duration: int):
    """
    Record sound using the microphone

    :param hal: The hardware abstraction object
    :param filename: The path of the file to record to
    :param duration: The time to record in seconds
    """
    pass


def record_video(hal: PizzaHAL, filename: str, duration: int):
    """
    Record video using the camera

    :param hal: The hardware abstraction object
    :param filename: The path of the file to record to
    :param duration: The time to record in seconds
    """
    pass


def take_photo(hal: PizzaHAL, filename: str):
    """
    Take a foto with the camera

    :param hal: The hardware abstraction object
    :param filename: The path of the filename for the foto
    """
    pass
