import click
from .statemachine import Statemachine


# TODO make click command
def main():
    sm = Statemachine()

    # TODO error handling, recovery/reboot
    sm.run()


if __name__=='__main__':
    main()
