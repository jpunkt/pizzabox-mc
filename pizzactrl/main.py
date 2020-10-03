import sys

import click
import logging

from .statemachine import Statemachine, State

logger = logging.getLogger('pizzactrl.main')


@click.command()
@click.option('--move', is_flag=True)
def main(move: bool=False):
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    sm = Statemachine(move)

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
