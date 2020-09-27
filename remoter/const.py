"""Constants for the Act on remote buttons integration."""
import itertools

DOMAIN = "remoter"

REPEATABLE_KEYS = ["KEY_VOLUMEUP", "KEY_VOLUMEDOWN", "KEY_REWIND", "KEY_FORWARD"]
UNREPEATABLE_KEYS = [
    f"KEY_{name}"
    for name in [
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


class RemoteButton:
    pass


for name in itertools.chain(REPEATABLE_KEYS, UNREPEATABLE_KEYS):
    setattr(RemoteButton, name, name)
