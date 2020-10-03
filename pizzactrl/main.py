import sys

import click
import logging

from .statemachine import Statemachine, State
from . import sb_de, sb_en

logger = logging.getLogger('pizzactrl.main')


@click.command()
@click.option('--move', is_flag=True)
@click.option('--test', is_flag=True, default=False)
def main(move: bool=False, test: bool = False):
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    sm = Statemachine(story_de=sb_de.STORYBOARD,
                      story_en=sb_en.STORYBOARD,
                      move=move)
    sm.test = test

    exitcode = 0
    try:
        sm.run()
    except Exception:
        logger.exception('An Error occurred while running the statemachine')
        exitcode = 1
    finally:
        if sm.state is State.ERROR:
            exitcode = 2
        del sm
        sys.exit(exitcode)


if __name__ == '__main__':
    main()
