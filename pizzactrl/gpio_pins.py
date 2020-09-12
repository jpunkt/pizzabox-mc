# GPIO pin definitions

BTN_BACK_GPIO = 6                    # "Back" button (user input)
BTN_FORWARD_GPIO = 5                 # "Forward" button (user input)

LED_BACK_BTN = 2                # LED in back-button
LED_FWD_BTN = 3                 # LED in forward-button

LID_SWITCH = 4                 # "Lid open" detector switch on front

LED_LAYER = 7                   # LED-strip for top layer
LED_BACKLIGHT = 8               # LED-strip for backlight

MOTOR_CTRL_UPDOWN = (20, 21, 19)   # Motor controller 1 (in1, in2, enable)
MOTOR_CTRL_LR = (22, 26, 27)       # Motor controller 2 (in1, in2, enable)

SCROLL_UPDOWN_SENSORS = (9, 10)  # Feed/Direction sensors
SCROLL_UPDOWN_ENDSTOP = 11       # End of Tape

SCROLL_LR_SENSORS = (13, 14)      # Feed/Direction sensors
SCROLL_LR_ENDSTOP = 15           # End of Tape
