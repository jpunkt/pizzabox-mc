from enum import Enum, auto

from .storyboard import Activity, StoryboardIterator

from .hal import *


class State(Enum):
    POWER_ON = auto()
    POST = auto()
    IDLE_START = auto()
    PLAY = auto()
    PAUSE = auto()
    IDLE_END = auto()
    SHUTDOWN = auto()
    ERROR = -1


class Statemachine:
    def __init__(self):
        self.state = State.POWER_ON
        self.hal = PizzaHAL()

    def run(self):
        choice = {
                State.POWER_ON: self._power_on,
                State.POST: self._post,
                State.IDLE_START: self._idle_start,
                State.PLAY: self._play,
                State.IDLE_END: self._idle_end,
                State.SHUTDOWN: self._shutdown
             }
        while self.state is not State.ERROR:
            choice[self.state]()
        # TODO log errors if possible
        self._shutdown()

    def _lid_open(self):
        """
        Callback for lid open sensor
        """
        if self.state is State.IDLE_START:
            self.state = State.PLAY

    def _lid_closed(self):
        """
        Callback for lid closed sensor
        """
        if self.state is State.POST:
            self.state = State.IDLE_START
        if self.state is State.PLAY:
            # TODO pause?
            pass
        if self.state is State.IDLE_END:
            self.state = State.SHUTDOWN

    def _power_on(self):
        """
        Initialize hal callbacks
        """
        self.hal.lid_sensor.when_pressed = self._lid_open
        self.hal.lid_sensor.when_released = self._lid_closed
        self.state = State.POST

    def _post(self):
        """
        Power on self test. Do not arm the device if the lid is open
        """
        if not self.hal.lid_sensor.value:
            self.state = State.IDLE_START

    def _idle_start(self):
        """
        Device is armed. Wait for user to open lid
        """
        pass

    def _wait_for_input(self):
        """
        Wait for user to press a button
        """
        pass

    def _play(self):
        """
        Run the storyboard
        """
        story = StoryboardIterator()
        for step in iter(story):
            if step.activity is Activity.WAIT_FOR_INPUT:
                wait_for_input(self.hal,
                               story.foward,
                               story.back,
                               step.values)
            else:
                {
                    Activity.PLAY_SOUND: play_sound,
                    Activity.PLAY_SOUND_INSERT: play_sound_insert,
                    Activity.RECORD_SOUND: record_sound,
                    Activity.RECORD_VIDEO: record_video,
                    Activity.TAKE_PHOTO: take_photo,
                    Activity.MOVE_UPDOWN: move_updown,
                    Activity.MOVE_LEFTRIGHT: move_leftright,
                    Activity.LIGHT_LAYER: light_layer,
                    Activity.LIGHT_BACK: backlight
                }[step.activity](self.hal, step.values)
                story.forward()
        rewind(self.hal)

    def _idle_end(self):
        """
        Wait for administrative shutdown or replay
        """
        pass

    def _shutdown(self):
        """
        Clean up, send system shutdown
        """
