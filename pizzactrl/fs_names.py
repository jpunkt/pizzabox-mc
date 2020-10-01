from enum import Enum

"""
Paths to files
"""
# Base paths
_STORY_SOUNDS = '/home/pi/sounds/'
_SFX_SOUNDS = 'sounds/'
_REC_FILES = '/home/pi/recordings/'     # TODO fill in recording target


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

    def __str__(self):
        """
        Get the context specific path

        :param context:
        :return:
        """
        return {
            FileType.STORY: lambda: (_STORY_SOUNDS + self.name + '.wav'),
            FileType.SFX: lambda: (_SFX_SOUNDS + self.name + '.wav'),
            FileType.REC: lambda: (_REC_FILES + self.name)
        }[self.filetype]()


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
REC_PORTRAIT = RecFile('portrait.jpg')
REC_CITY_NAME = RecFile('city_name.wav')
REC_CITY_DESC = RecFile('city_description.wav')
REC_CITY_SOUND = RecFile('city_sound.wav')
REC_DRAW_CITY = RecFile('city_video.h264')

SFX_ERROR = SfxFile('error')
SFX_POST_OK = SfxFile('post_ok')
SFX_SHUTTER = SfxFile('shutter')

SND_SELECT_LANG = StoryFile(name='01de')
