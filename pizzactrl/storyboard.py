from enum import Enum, auto

from pizzactrl import fs_names


class Activity(Enum):
    WAIT_FOR_INPUT = {'steps': 0},
    PLAY_SOUND = {'sound': None},
    PLAY_SOUND_INSERT = {'sound_1': None, 'insert': None, 'sound_2': None},
    RECORD_SOUND = {'duration': 0.0, 'filename': ''},
    RECORD_VIDEO = {'duration': 0.0, 'filename': ''},
    TAKE_PHOTO = {'filename': ''},
    MOVE_UPDOWN = {'distance': 0.0, 'speed': 0.0},
    MOVE_LEFTRIGHT = {'distance': 0.0, 'speed': 0.0},
    LIGHT_LAYER = {'brightness': 1.0},
    LIGHT_BACK = {'brightness': 1.0},


class Do:
    def __init__(self, activity: Activity, **kwargs):
        self.activity = activity
        self.values = {}
        for key, value in activity.value.items():
            self.values[key] = kwargs.get(key, value)


class StoryboardIterator:
    """
    Iterates over the storyboard. Only moves forward if `forward()` was called.
    `back(0)` does not advance, `back(3)` moves backward by 3 items.
    """
    def __init__(self):
        self.pos = 0

    def __iter__(self):
        return self

    def __next__(self) -> Do:
        if self.pos >= len(Storyboard):
            raise StopIteration
        return Storyboard[self.pos]

    def forward(self):
        self.pos += 1

    def back(self, steps):
        if self.pos > 0:
            self.pos -= steps


Storyboard = [
    Do(Activity.PLAY_SOUND, sound=fs_names.SND_INTRO),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.PLAY_SOUND, sound='sound/intro.wav'),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.PLAY_SOUND, sound='sound/record_name.wav'),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.RECORD_SOUND, duration=10.0, filename='output/name.wav'),
    Do(Activity.PLAY_SOUND),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.RECORD_SOUND, duration=60.0, filename='output/my_ibk.wav'),
    Do(Activity.PLAY_SOUND, sound='sound/take_photo.wav'),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.TAKE_PHOTO, filename='output/portrait.jpg'),
    Do(Activity.PLAY_SOUND_INSERT, sound_1='sound/townintro-1.wav',
       insert='output/name.wav', sound_2='sound/townintro-2.wav'),
    Do(Activity.PLAY_SOUND, sound='sound/carmen.wav'),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.PLAY_SOUND, sound='sound/krys.wav'),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.PLAY_SOUND, sound='sound/pistor.wav'),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.PLAY_SOUND, sound='sound/guia.wav'),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.PLAY_SOUND, sound='sound/uebung.wav'),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.PLAY_SOUND, sound='sound/city_name.wav'),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.RECORD_SOUND, filename='output/city_name.wav', duration=10.0),
    Do(Activity.PLAY_SOUND_INSERT, sound_1='sound/city_description-1.wav',
       insert='output/city_name.wav', sound_2='sound/city_desciption-2.wav'),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.RECORD_SOUND, filename='output/city_description.wav',
       duration= 60.0),
    Do(Activity.PLAY_SOUND, sound='sound/city_sound.wav'),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.RECORD_SOUND, filename='output/city_sound.wav', duration=60.0),
    Do(Activity.PLAY_SOUND, sound='sound/draw_city.wav'),
    Do(Activity.WAIT_FOR_INPUT),
    Do(Activity.RECORD_VIDEO, filename='output/city_video.mp4', duration=60.0),
    Do(Activity.PLAY_SOUND, sound='sound/thankyou.wav')
]

