import logging
from pprint import pformat

from homeassistant.components import media_player
from homeassistant.components.androidtv.media_player import SERVICE_ADB_COMMAND, ANDROIDTV_DOMAIN
from homeassistant.const import ATTR_COMMAND, SERVICE_MEDIA_PLAY_PAUSE

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
# Actually, there are only two numbers that change from one to the next. If we call them num1 and num2, then
# the command is:
# FIRETV_COMMAND = f"""sendevent /dev/input/event3 4 4 {num1} && sendevent /dev/input/event3 1 {num2} 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 {num1} && sendevent /dev/input/event3 1 {num2} 0 && sendevent /dev/input/event3 0 0 0"""

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


class FireStickSources:
    hbomax = "com.hbo.hbonow"
    home = "com.amazon.tv.launcher"
    jellyfin = "Jellyfin"
    prime = "Amazon Video"
    qvc = "com.qvc.firetv"


class FireStick(MyDevice):
    domain = media_player.DOMAIN
    entity_id = f"{domain}.amazon_firestick"  # media_player.amazon_firestick
    on_states = ["on", "standby", "playing", "idle"]
    sources = FireStickSources()

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
    from androidtv.constants import KEYS

    keymap = {
        RemoteButton.KEY_UP: KEYS["UP"],
        RemoteButton.KEY_DOWN: KEYS["DOWN"],
        RemoteButton.KEY_LEFT: KEYS["LEFT"],
        RemoteButton.KEY_RIGHT: KEYS["RIGHT"],
        RemoteButton.KEY_OK: KEYS["CENTER"],
        RemoteButton.KEY_BACK: KEYS["BACK"],
        RemoteButton.KEY_HOME: KEYS["HOME"],
        RemoteButton.KEY_MENU: KEYS["MENU"],
        RemoteButton.KEY_REWIND: KEYS["REWIND"],
        RemoteButton.KEY_FORWARD: KEYS["FAST_FORWARD"],
        # RemoteButton.KEY_PAUSE: KEYS["PAUSE"],
    }

    async def send_remote_button(self, name):
        # name should be a key from RemoteButton
        if name in (RemoteButton.KEY_PLAY, RemoteButton.KEY_PAUSE):
            return self._service(service=SERVICE_MEDIA_PLAY_PAUSE)

        # 'input keyevent {0}'.format(key)
        return await self._service(
            domain=ANDROIDTV_DOMAIN,
            service=SERVICE_ADB_COMMAND,
            command="input keyevent {0}".format(self.keymap[name]),
        )
        #
        # if name == RemoteButton.KEY_DOWN:
        #
        #
        # if name == RemoteButton.KEY_RECORD:
        #     # Press RECORD, then within  a few seconds press a button on the real
        #     # firetv remote. Within 10 seconds, a notification should appear in homeassistant
        #     # containing a string of 'sendevent' commands that can be used to more quickly
        #     # have the same effect as that firestick remote button.
        #     logger.warning(
        #         "RECORDING for 8 seconds... press ONE BUTTON on the REAL Firetv remote"
        #     )
        #     return await self._service("learn_sendevent", domain="androidtv")
        # else:
        #     return await self._service("adb_command", domain="androidtv", command=self.keymap[name])

    async def set_source(self, source):
        logger.warning(
            f"-------------------------------------\n"
            f"FIRESTICK\n"
            f"STATE\n"
            f"{pformat(self.state.as_dict())}"
        )
        # If it's not on, it needs to be
        if not self.is_on():
            await self.turn_on()
        logger.warning(f"Setting source for f{self.entity_id} to {source}")
        return await self._service(service="select_source", source=source)

    # _FIRETV_KEY_COMMANDS = {
    #     "POWER": """sendevent /dev/input/event3 4 4 458854 && sendevent /dev/input/event3 1 116 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458854 && sendevent /dev/input/event3 1 116 0 && sendevent /dev/input/event3 0 0 0""",
    #     "MIC": """sendevent /dev/input/event3 4 4 786977 && sendevent /dev/input/event3 1 217 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786977 && sendevent /dev/input/event3 1 217 0 && sendevent /dev/input/event3 0 0 0""",
    #     "UP": """sendevent /dev/input/event3 4 4 458834 && sendevent /dev/input/event3 1 103 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458834 && sendevent /dev/input/event3 1 103 0 && sendevent /dev/input/event3 0 0 0""",
    #     "LEFT": """sendevent /dev/input/event3 4 4 458832 && sendevent /dev/input/event3 1 105 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458832 && sendevent /dev/input/event3 1 105 0 && sendevent /dev/input/event3 0 0 0""",
    #     "OK": """sendevent /dev/input/event3 4 4 458840 && sendevent /dev/input/event3 1 96 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458840 && sendevent /dev/input/event3 1 96 0 && sendevent /dev/input/event3 0 0 0""",
    #     "RIGHT": """sendevent /dev/input/event3 4 4 458831 && sendevent /dev/input/event3 1 106 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458831 && sendevent /dev/input/event3 1 106 0 && sendevent /dev/input/event3 0 0 0""",
    #     "DOWN": """sendevent /dev/input/event3 4 4 458833 && sendevent /dev/input/event3 1 108 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458833 && sendevent /dev/input/event3 1 108 0 && sendevent /dev/input/event3 0 0 0""",
    #     "BACK_ARROW": """sendevent /dev/input/event3 4 4 458993 && sendevent /dev/input/event3 1 158 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 458993 && sendevent /dev/input/event3 1 158 0 && sendevent /dev/input/event3 0 0 0""",
    #     "HOME": """sendevent /dev/input/event3 4 4 786979 && sendevent /dev/input/event3 1 172 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786979 && sendevent /dev/input/event3 1 172 0 && sendevent /dev/input/event3 0 0 0""",
    #     "MENU": """sendevent /dev/input/event3 4 4 786496 && sendevent /dev/input/event3 1 139 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786496 && sendevent /dev/input/event3 1 139 0 && sendevent /dev/input/event3 0 0 0""",
    #     "REW": """sendevent /dev/input/event3 4 4 786612 && sendevent /dev/input/event3 1 168 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786612 && sendevent /dev/input/event3 1 168 0 && sendevent /dev/input/event3 0 0 0""",
    #     "PLAY_PAUSE": """sendevent /dev/input/event3 4 4 786637 && sendevent /dev/input/event3 1 164 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786637 && sendevent /dev/input/event3 1 164 0 && sendevent /dev/input/event3 0 0 0""",
    #     "FF": """sendevent /dev/input/event3 4 4 786611 && sendevent /dev/input/event3 1 208 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786611 && sendevent /dev/input/event3 1 208 0 && sendevent /dev/input/event3 0 0 0""",
    #     "PLUS": """sendevent /dev/input/event3 4 4 786665 && sendevent /dev/input/event3 1 115 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786665 && sendevent /dev/input/event3 1 115 0 && sendevent /dev/input/event3 0 0 0""",
    #     "MINUS": """sendevent /dev/input/event3 4 4 786666 && sendevent /dev/input/event3 1 114 1 && sendevent /dev/input/event3 0 0 0 && sendevent /dev/input/event3 4 4 786666 && sendevent /dev/input/event3 1 114 0 && sendevent /dev/input/event3 0 0 0""",
    #     # FIRETV_MUTE does not seem to register, not that we need it.
    # }
    #
    # # https://developer.android.com/reference/android/view/KeyEvent
    # keymap = {
    #     RemoteButton.KEY_HOME: _FIRETV_KEY_COMMANDS["HOME"],
    #     RemoteButton.KEY_UP: _FIRETV_KEY_COMMANDS["UP"],
    #     RemoteButton.KEY_DOWN: _FIRETV_KEY_COMMANDS["DOWN"],
    #     RemoteButton.KEY_LEFT: _FIRETV_KEY_COMMANDS["LEFT"],
    #     RemoteButton.KEY_RIGHT: _FIRETV_KEY_COMMANDS["RIGHT"],
    #     RemoteButton.KEY_OK: _FIRETV_KEY_COMMANDS["OK"],
    #     RemoteButton.KEY_PLAY: _FIRETV_KEY_COMMANDS["PLAY_PAUSE"],
    #     RemoteButton.KEY_PAUSE: _FIRETV_KEY_COMMANDS["PLAY_PAUSE"],
    #     RemoteButton.KEY_REWIND: _FIRETV_KEY_COMMANDS["REW"],
    #     RemoteButton.KEY_FORWARD: _FIRETV_KEY_COMMANDS["FF"],
    #     RemoteButton.KEY_RECORD: None,  # It's supported, but we handle it specially in send_remote_button().
    # }


#     async def inspect_firestick():
#         androidtv_entity = list(hass.data["androidtv"].values())[0]
#         logger.warning(f"_get_sources = {androidtv_entity._get_sources}")
#         # logger.warning(type(androidtv_entity))
#         # <class 'homeassistant.components.androidtv.media_player.FireTVDevice'>
#         # None
#         await firestick.turn_on()
#         count = 0
#         while count < 10:
#             await androidtv_entity.async_update()
#             if androidtv_entity.source_list is not None:
#                 logger.warning("Firestick .source_list")
#                 logger.warning(androidtv_entity.source_list)
#                 break
#             count += 1
#             await asyncio.sleep(1)
#     do(inspect_firestick())
#
