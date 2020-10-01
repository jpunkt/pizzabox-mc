from . import fs_names
from . import storyboard

STORYBOARD = [
    storyboard.Chapter(
        storyboard.Do(storyboard.Activity.PLAY_SOUND,
                      sound=fs_names.StoryFile('01dummy')),
        storyboard.Do(storyboard.Activity.WAIT_FOR_INPUT)
    ),
    # storyboard.Chapter(
    #     storyboard.Do(storyboard.Activity.PLAY_SOUND,
    #                   sound=fs_names.StoryFile('02dummy')),
    #     storyboard.Do(storyboard.Activity.LIGHT_BACK,
    #                   intensity=1.0, fade=1.0),
    #     storyboard.Do(storyboard.Activity.PLAY_SOUND,
    #                   sound=fs_names.StoryFile('03dummy')),
    #     storyboard.Do(storyboard.Activity.LIGHT_BACK,
    #                   intensity=.0, fade=1.0),
    #     storyboard.Do(storyboard.Activity.WAIT_FOR_INPUT)
    # ),
    # storyboard.Chapter(
    #     storyboard.Do(storyboard.Activity.PLAY_SOUND,
    #                   sound=fs_names.StoryFile('04dummy')),
    #     storyboard.Do(storyboard.Activity.WAIT_FOR_INPUT),
    #     storyboard.Do(storyboard.Activity.RECORD_SOUND,
    #                   filename=fs_names.RecFile('name.wav'), duration=5.0)
    # ),
    # storyboard.Chapter(
    #     storyboard.Do(storyboard.Activity.PLAY_SOUND,
    #                   sound=fs_names.StoryFile('05dummy')),
    #     storyboard.Do(storyboard.Activity.PLAY_SOUND,
    #                   sound=fs_names.RecFile('name.wav')),
    #     storyboard.Do(storyboard.Activity.PLAY_SOUND,
    #                   sound=fs_names.StoryFile('06dummy'))
    # )
    # storyboard.Chapter(
    #     storyboard.Do(storyboard.Activity.WAIT_FOR_INPUT),
    #     storyboard.Do(storyboard.Activity.TAKE_PHOTO,
    #                   filename=fs_names.REC_PORTRAIT)
    # )
    # storyboard.Chapter(
    #     storyboard.Do(storyboard.Activity.WAIT_FOR_INPUT),
    #     storyboard.Do(storyboard.Activity.RECORD_VIDEO,
    #                   filename=fs_names.REC_DRAW_CITY,
    #                   duration=10.0)
    # )
    storyboard.Chapter(
        storyboard.Do(storyboard.Activity.PLAY_SOUND,
                      sound=fs_names.StoryFile('07dummy')),
        storyboard.Do(storyboard.Activity.ADVANCE_UP,
                      distance=10),
        storyboard.Do(storyboard.Activity.PLAY_SOUND,
                      sound=fs_names.SfxFile('stop'))
    )
]

