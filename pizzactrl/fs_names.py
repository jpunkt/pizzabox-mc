from enum import Enum

"""
Paths to files
"""


class FileType(Enum):
    REC = 'r'
    STORY = 's'
    SFX = 'f'


class FileHandle:
    """
    Base class for handles on context-specific paths
    """

    def __init__(self, name: str, filetype: FileType):
        self.name = name
        self.filetype = filetype

    def get_path(self, context):
        """
        Get the context specific path

        :param context:
        :return:
        """
        pass


class SfxFile(FileHandle):
    """
    Returns the path to a sound-effect file
    """
    def __init__(self, name: str):
        FileHandle.__init__(self, name, FileType.SFX)


class RecFile(FileHandle):
    """
    Returns the path to a recordable file
    """
    def __init__(self, name: str):
        FileHandle.__init__(self, name, FileType.REC)


class StoryFile(FileHandle):
    """
    Returns the path to a storyboard file
    """
    def __init__(self, name: str):
        FileHandle.__init__(self, name, FileType.STORY)


REC_NAME = RecFile('name.wav')
REC_MY_IBK = RecFile('my_ibk.wav')
REC_PORTRAIT = 'output/portrait.jpg'
REC_CITY_NAME = 'output/city_name.wav'
REC_CITY_DESC = 'output/city_description.wav'
REC_CITY_SOUND = 'output/city_sound.wav'
REC_DRAW_CITY = 'output/city_video.mp4'

SND_WELCOME = StoryFile('welcome.wav')
SND_INTRO = 'sound/intro.wav'
SND_RECORD_NAME = 'sound/record_name.wav'
SND_PHOTO = 'sound/take_photo.wav'
SND_TOWNINTRO_1 = 'sound/townintro-1.wav'
SND_TOWNINTRO_2 = 'sound/townintro-2.wav'
SND_CARMEN = 'sound/carmen.wav'
SND_KRYS = 'sound/krys.wav'
SND_PISTOR = 'sound/pistor.wav'
SND_GUIA = 'sound/guia.wav'
SND_UEBUNG = 'sound/uebung.wav'
SND_CITY_NAME = 'sound/city_name.wav'
SND_CITY_DESC_1 = 'sound/city_description-1.wav'
SND_CITY_DESC_2 = 'sound/city_desciption-2.wav'
SND_CITY_SOUND = 'sound/city_sound.wav'
SND_DRAW_CITY = 'sound/draw_city.wav'
SND_THANK_YOU = 'sound/thankyou.wav'
SND_GOOD_BYE = StoryFile('goodbye.wav')

SFX_POST_OK = SfxFile('post_ok.wav')
SFX_SHUTTER = SfxFile('shutter.wav')
SFX_CLOSE_LID_REMINDER = SfxFile('close_lid.wav')


