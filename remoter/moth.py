# moth is a laptop with HDMI out I use to watch videos
import requests

from remoter import RemoteButton


class Moth:
    current_source = ""

    def __init__(self, hass):
        self.hass = hass

    @property
    def supported_keys(self):
        return [
            RemoteButton.KEY_PLAY,
            RemoteButton.KEY_PAUSE,
            RemoteButton.KEY_UP,
            RemoteButton.KEY_DOWN,
            RemoteButton.KEY_LEFT,
            RemoteButton.KEY_RIGHT,
        ]

    def send_remote_button(self, name):
        r = requests.post(f"http://192.168.1.2/postbutton/{name}/")
        r.raise_for_status()
