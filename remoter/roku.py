import logging

from homeassistant.components import remote, media_player

from .const import RemoteButton
from .mydevice import MyDevice

logger = logging.getLogger(__name__)

SERVICE_SEND_COMMAND = "send_command"

ROKU_REMOTE_BUTTON_TO_SERVICE = {
    RemoteButton.KEY_UP: "up",
    RemoteButton.KEY_DOWN: "down",
    RemoteButton.KEY_LEFT: "left",
    RemoteButton.KEY_RIGHT: "right",
    RemoteButton.KEY_EXIT: "home",
    RemoteButton.KEY_OK: "select",
    RemoteButton.KEY_PLAY: "play",
    RemoteButton.KEY_PAUSE: "play",
    RemoteButton.KEY_MENU: "back",
}

"""
For media_player.55_tcl_roku_tv, valid services are dict_keys(
['turn_on', 'turn_off', 'toggle', 'volume_up', 'volume_down', 'media_play_pause', 'media_play', 'media_pause', 
'media_stop', 'media_next_track', 'media_previous_track', 'clear_playlist', 'volume_set', 'volume_mute', 
'media_seek', 'select_source', 'select_sound_mode', 'play_media', 'shuffle_set'])

For remote.55_tcl_roku_tv, valid services are dict_keys(
['turn_off', 'turn_on', 'toggle', 'send_command', 'learn_command'])
"""

class RokuRemote(MyDevice):
    domain = remote.DOMAIN
    entity_id = f"{domain}.55_tcl_roku_tv"

    @property
    def supported_keys(self):
        return ROKU_REMOTE_BUTTON_TO_SERVICE.keys()

    async def send_key(self, key):
        return await self._service(service="send_command", command=ROKU_REMOTE_BUTTON_TO_SERVICE[key],)


class Roku(MyDevice):
    domain = media_player.DOMAIN
    entity_id = f"{domain}.55_tcl_roku_tv"
    on_states = ["home", "on"]

    def __init__(self, hass):
        super().__init__(hass)
        self.remote = RokuRemote(hass)

    @property
    def supported_keys(self):
        return self.remote.supported_keys

    async def send_key(self, key):
        return await self.remote.send_key(key)

    async def set_source(self, source):
        # If it's not on, it needs to be
        logger.warning(f"ROKU SET SOURCE {source}")
        if source not in self.state.attributes["source_list"]:
            logger.error(f"ROKU: source {source!r} is not valid. Choices are {self.state.attributes['source_list']!r}")
            return
        if not self.is_on():
            await self.turn_on()
        await self._service(service="select_source", source=source)
