import click
from .statemachine import Statemachine


# TODO make click command
def main():
    sm = Statemachine()

    try:
        sm.run()
    except Exception:
        # TODO error handling, recovery/reboot
        pass
    finally:
        del sm
        # TODO shut down raspberry


if __name__=='__main__':
    main()
