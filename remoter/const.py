"""Constants for the Act on remote buttons integration."""
DOMAIN = "remoter"


class RemoteButton:
    KEY_VOLUMEUP = "KEY_VOLUMEUP"
    KEY_VOLUMEDOWN = "KEY_VOLUMEDOWN"
    KEY_REWIND = "KEY_REWIND"
    KEY_FORWARD = "KEY_FORWARD"
    KEY_POWER = "KEY_POWER"
    KEY_MUTE = "KEY_MUTE"
    KEY_CHANNELUP = "KEY_CHANNELUP"
    KEY_CHANNELDOWN = "KEY_CHANNELDOWN"
    KEY_RED = "KEY_RED"
    KEY_GREEN = "KEY_GREEN"
    KEY_YELLOW = "KEY_YELLOW"
    KEY_BLUE = "KEY_BLUE"
    KEY_1 = "KEY_1"
    KEY_2 = "KEY_2"
    KEY_3 = "KEY_3"
    KEY_4 = "KEY_4"
    KEY_5 = "KEY_5"
    KEY_6 = "KEY_6"
    KEY_7 = "KEY_7"
    KEY_8 = "KEY_8"
    KEY_9 = "KEY_9"
    KEY_0 = "KEY_0"
    KEY_UP = "KEY_UP"
    KEY_LEFT = "KEY_LEFT"
    KEY_OK = "KEY_OK"
    KEY_RIGHT = "KEY_RIGHT"
    KEY_DOWN = "KEY_DOWN"
    KEY_MENU = "KEY_MENU"
    KEY_BACK = KEY_MENU
    KEY_EXIT = "KEY_EXIT"
    KEY_HOME = KEY_EXIT
    KEY_PLAY = "KEY_PLAY"
    KEY_PAUSE = "KEY_PAUSE"
    KEY_STOP = "KEY_STOP"
    KEY_PREVIOUS = "KEY_PREVIOUS"
    KEY_NEXT = "KEY_NEXT"
    KEY_RECORD = "KEY_RECORD"

    REPEATABLE_KEYS = []
    UNREPEATABLE_KEYS = [
        f"KEY_{name}"
        for name in [
            "VOLUMEUP",
            "VOLUMEDOWN",
            "REWIND",
            "FORWARD",
            "POWER",
            "MUTE",
            "CHANNELUP",
            "CHANNELDOWN",
            "RED",
            "GREEN",
            "YELLOW",
            "BLUE",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "0",
            "UP",
            "LEFT",
            "OK",
            "RIGHT",
            "DOWN",
            "MENU",
            "EXIT",
            "PLAY",
            "PAUSE",
            "STOP",
            "PREVIOUS",
            "NEXT",
            "RECORD",
        ]
    ]
