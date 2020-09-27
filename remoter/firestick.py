import logging
from pprint import pformat

from homeassistant.components import media_player

from .const import RemoteButton
from .mydevice import MyDevice

logger = logging.getLogger(__name__)

# Map remote button names, to the key names we need to use to send to
# the fire stick (fire tv)
FIRESTICK_REMOTE_BUTTON_TO_KEY = {
    RemoteButton.KEY_EXIT: "MOVE_HOME",
    RemoteButton.KEY_OK: "CENTER",
    RemoteButton.KEY_MENU: "BACK",
}
# for key_name in ANDROIDTV_KEYS.keys():
#     FIRESTICK_REMOTE_BUTTON_TO_KEY[f"KEY_{key_name}"] = key_name

# These are the buttons on the Firestick Remote and the result of "learn_sendevent" for each for my 4K Firestick.
# They're in order top to bottom.
FIRETV_POWER = """sendevent /dev/input/event3 4 4 458854 && sendevent /dev/input/event3 1 116 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458854 && sendevent /dev/input/event3 1 116 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_MIC = """sendevent /dev/input/event3 4 4 786977 && sendevent /dev/input/event3 1 217 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786977 && sendevent /dev/input/event3 1 217 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_UP = """sendevent /dev/input/event3 4 4 458834 && sendevent /dev/input/event3 1 103 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458834 && sendevent /dev/input/event3 1 103 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_LEFT = """sendevent /dev/input/event3 4 4 458832 && sendevent /dev/input/event3 1 105 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458832 && sendevent /dev/input/event3 1 105 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_OK = """sendevent /dev/input/event3 4 4 458840 && sendevent /dev/input/event3 1 96 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458840 && sendevent /dev/input/event3 1 96 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_RIGHT = """sendevent /dev/input/event3 4 4 458832 && sendevent /dev/input/event3 1 105 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458832 && sendevent /dev/input/event3 1 105 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_DOWN = """sendevent /dev/input/event3 4 4 458833 && sendevent /dev/input/event3 1 108 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458833 && sendevent /dev/input/event3 1 108 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_BACK_ARROW = """sendevent /dev/input/event3 4 4 458993 && sendevent /dev/input/event3 1 158 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458993 && sendevent /dev/input/event3 1 158 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_HOME = """sendevent /dev/input/event3 4 4 786979 && sendevent /dev/input/event3 1 172 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786979 && sendevent /dev/input/event3 1 172 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_HAMBURGER = """sendevent /dev/input/event3 4 4 786496 && sendevent /dev/input/event3 1 139 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786496 && sendevent /dev/input/event3 1 139 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_REW = """sendevent /dev/input/event3 4 4 786612 && sendevent /dev/input/event3 1 168 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786612 && sendevent /dev/input/event3 1 168 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_PLAY_PAUSE = """sendevent /dev/input/event3 4 4 786637 && sendevent /dev/input/event3 1 164 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786637 && sendevent /dev/input/event3 1 164 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_FF = """sendevent /dev/input/event3 4 4 786611 && sendevent /dev/input/event3 1 208 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786611 && sendevent /dev/input/event3 1 208 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_PLUS = """sendevent /dev/input/event3 4 4 786665 && sendevent /dev/input/event3 1 115 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786665 && sendevent /dev/input/event3 1 115 0 && sendevent /dev/input/event3 0 0 0"""
FIRETV_MINUS = """sendevent /dev/input/event3 4 4 786666 && sendevent /dev/input/event3 1 114 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786666 && sendevent /dev/input/event3 1 114 0 && sendevent /dev/input/event3 0 0 0"""
# FIRETV_MUTE does not seem to register, not that we need it.

FIRESTICK_REMOTE_BUTTON_TO_KEY[RemoteButton.KEY_LEFT] = FIRETV_LEFT
FIRESTICK_REMOTE_BUTTON_TO_KEY[RemoteButton.KEY_RIGHT] = FIRETV_RIGHT
FIRESTICK_REMOTE_BUTTON_TO_KEY[RemoteButton.KEY_UP] = FIRETV_UP
FIRESTICK_REMOTE_BUTTON_TO_KEY[RemoteButton.KEY_DOWN] = FIRETV_DOWN
FIRESTICK_REMOTE_BUTTON_TO_KEY[RemoteButton.KEY_OK] = FIRETV_OK
FIRESTICK_REMOTE_BUTTON_TO_KEY[RemoteButton.KEY_PLAY] = FIRETV_PLAY_PAUSE
FIRESTICK_REMOTE_BUTTON_TO_KEY[RemoteButton.KEY_PAUSE] = FIRETV_PLAY_PAUSE
FIRESTICK_REMOTE_BUTTON_TO_KEY[RemoteButton.KEY_MENU] = FIRETV_BACK_ARROW
FIRESTICK_REMOTE_BUTTON_TO_KEY[RemoteButton.KEY_EXIT] = FIRETV_HOME
FIRESTICK_REMOTE_BUTTON_TO_KEY[RemoteButton.KEY_REWIND] = FIRETV_REW
FIRESTICK_REMOTE_BUTTON_TO_KEY[RemoteButton.KEY_FORWARD] = FIRETV_FF

"""
I am still trying to figure out how to get the live source_list.
Here's a snapshot that Homeassistant somehow fetched and included in a scene.

      source_list:
      - com.amazon.imp
      - android.ext.services
      - com.android.proxyhandler
      - com.amazon.tcomm
      - com.amazon.whad
      - com.amazon.client.metrics
      - com.amazon.tv.ime
      - logcat
      - com.amazon.alexa.externalmediaplayer.fireos
      - com.amazon.device.rdmapplication
      - com.amazon.alta.h2clientservice
      - com.amazon.venezia
      - com.amazon.kso.blackbird
      - com.qvc.firetv
      - com.amazon.whisperlink.core.android
      - com.amazon.whisperjoin.middleware.np
      - com.amazon.ftv.xpicker
      - com.amazon.whisperjoin.wss.wifiprovisioner
      - com.amazon.device.messaging
      - com.amazon.discoveryservice.core.android
      - com.amazon.connectivitycontroller
      - com.amazon.tv.alexaalerts
      - com.amazon.tv.livetv
      - com.amazon.wirelessmetrics.service
      - com.amazon.device.bluetoothkeymaplib
      - com.amazon.uxcontrollerservice
      - com.amazon.uxnotification
      - com.amazon.autopairservice
      - com.amazon.tv.notificationcenter
      - com.amazon.firebat
      - com.amazon.tv.launcher
      - com.amazon.vizzini
      - com.amazon.webview.chromium:AWVArcusServiceProcess
      - com.amazon.webview.chromium:AWVMetricsProcess
      - com.amazon.tv.devicecontrol
      - Amazon Video
      - com.amazon.diode
      - com.amazon.ceviche
"""

"""
For media_player.amazon_firestick, valid services are dict_keys(
['turn_on', 'turn_off', 'toggle', 'volume_up', 'volume_down', 'media_play_pause', 'media_play', 'media_pause', 
'media_stop', 'media_next_track', 'media_previous_track', 'clear_playlist', 'volume_set', 'volume_mute', 
'media_seek', 'select_source', 'select_sound_mode', 'play_media', 'shuffle_set'])
"""

class FireStick(MyDevice):
    domain = media_player.DOMAIN
    entity_id = f"{domain}.amazon_firestick"
    on_states = ["on", "standby"]

    """
     {
     'entity_id': 'media_player.amazon_firestick', 
     'state': 'unknown', 
     'attributes': {
         'adb_response': None, 
         'friendly_name': 'Amazon Firestick', 
         'entity_picture': '/api/media_player_proxy/media_player.amazon_firestick?token=952a954ce7be7ec398492152f1bfd98b59c5ab0a32a6d6dccfc6315e56b28a1f&cache=1601130931.160467', 
         'supported_features': 22961
     }, 
     'last_changed': datetime.datetime(2020, 9, 26, 14, 35, 31, 160583, tzinfo=<UTC>), 
     'last_updated': datetime.datetime(2020, 9, 26, 14, 35, 31, 160583, tzinfo=<UTC>), 
     'context': {
        'id': '87697b06000511eb8b915f255c94b82d', 
        'parent_id': None, 
        'user_id': None
        }
    }
    """

    async def send_key(self, name):
        logger.warning(f"Send firestick key {name}")
        return await self._service("adb_command", command=FIRESTICK_REMOTE_BUTTON_TO_KEY[name])

    async def learn_sendevent(self):
        return await self._service("learn_sendevent")

    @property
    def supported_keys(self):
        return FIRESTICK_REMOTE_BUTTON_TO_KEY.keys()

    async def set_source(self, source):
        logger.warning(f"-------------------------------------\n"
                       f"FIRESTICK\n"
                       f"STATE\n"
                       f"{pformat(self.state.as_dict())}"
                       )
        # If it's not on, it needs to be
        if not self.is_on():
            await self.turn_on()
        logger.warning(f"Setting source for f{self.entity_id} to {source}")
        return await self._service(service="select_source", source=source)
