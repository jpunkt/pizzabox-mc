import logging

from enum import Enum, auto

from pizzactrl import fs_names, sb_dummy
from .storyboard import Activity

from .hal import *

logger = logging.getLogger(__name__)


class State(Enum):
    POWER_ON = auto()
    POST = auto()
    IDLE_START = auto()
    PLAY = auto()
    PAUSE = auto()
    IDLE_END = auto()
    SHUTDOWN = auto()
    ERROR = -1


def load_sounds():
    """
    Load all prerecorded Sounds from the cache

    TODO implement
    :returns a list of sound file names
    """

    return []


def foto(hal: PizzaHAL, filename: str):
    """
    Play a sound and then make a photo

    :param hal:
    :param filename:
    :return:
    """
    sleep(0.5)
    play_sound(hal, fs_names.SFX_SHUTTER)
    take_photo(hal, filename)


def video(hal: PizzaHAL, filename: Any, duration: float = 10.0):
    sleep(0.5)
    play_sound(hal, fs_names.SFX_SHUTTER)
    record_video(hal, filename, duration)


class Statemachine:
    def __init__(self):
        self.state = State.POWER_ON
        self.hal = PizzaHAL()
        self.story = None

    def run(self):
        logger.debug(f'Run(state={self.state})')
        choice = {
                State.POWER_ON: self._power_on,
                State.POST: self._post,
                State.IDLE_START: self._idle_start,  # TODO implement with callbacks
                State.PLAY: self._play,
                State.IDLE_END: self._idle_end   # TODO implement with callbacks
             }
        while (self.state is not State.ERROR) and \
                (self.state is not State.SHUTDOWN):
            choice[self.state]()
        if self.state is State.ERROR:
            # TODO log errors if possible
            play_sound(self.hal, fs_names.SFX_ERROR)

        self._shutdown()

    def _lang_de(self):
        logger.debug(f'select language german')
        self.story = sb_dummy.STORYBOARD

    def _lang_en(self):
        logger.debug(f'select language english')
        self.story = None

    def _power_on(self):
        """
        Initialize hal callbacks, load sounds
        """
        logger.debug(f'power on')
        # self.hal.lid_sensor.when_pressed = self._lid_open
        # self.hal.lid_sensor.when_released = self._lid_closed
        init_sounds(self.hal, load_sounds())
        init_camera(self.hal)
        self.state = State.POST

    def _post(self):
        """
        Power on self test.
        """
        logger.debug(f'post')
        # check scroll positions and rewind if necessary
        rewind(self.hal)

        # TODO check if USB-Stick is present

        # play a sound if everything is alright
        play_sound(self.hal, fs_names.SFX_POST_OK)

        # TODO set callback for blue button

        self.hal.btn_forward.when_deactivated = self._start

        self.state = State.IDLE_START

    def _idle_start(self):
        """
        Device is armed. Wait for user to press both buttons to start
        """
        pass

    def _start(self):
        """
        Start playback when both buttons are held for 3s
        :return:
        """
        t = 0.
        while (self.hal.btn_forward.inactive_time < 3.0) and \
                not self.hal.btn_forward.is_active:
            t = self.hal.btn_forward.inactive_time

        if t > 3.0:
            self.hal.btn_forward.when_held = None
            self.state = State.PLAY

    def _play(self):
        """
        Run the storyboard
        """
        logger.debug(f'play')
        # TODO select language
        # TODO implement chapters
        play_sound(self.hal, fs_names.SND_SELECT_LANG)
        wait_for_input(self.hal,
                       self._lang_de,
                       self._lang_en)

        sleep(0.5)

        if self.story is None:
            self.story = sb_dummy.STORYBOARD

        for chapter in iter(self.story):
            while chapter.hasnext():
                act = next(chapter)
                if act.activity is Activity.WAIT_FOR_INPUT:
                    wait_for_input(self.hal,
                                   None,
                                   chapter.rewind)
                else:
                    {
                        Activity.PLAY_SOUND: play_sound,
                        Activity.RECORD_SOUND: record_sound,
                        Activity.RECORD_VIDEO: record_video,
                        Activity.TAKE_PHOTO: foto,
                        Activity.LIGHT_LAYER: light_layer,
                        Activity.LIGHT_BACK: backlight,
                        Activity.ADVANCE_UP: move_updown,
                    }[act.activity](self.hal, **act.values)

        self.state = State.IDLE_END

    def _idle_end(self):
        """
        Initialize shutdown
        """
        self.state = State.SHUTDOWN
        pass

    def _shutdown(self):
        """
        Clean up, end execution
        """
        logger.debug('shutdown')
        del self.hal
