import asyncio
import logging

from homeassistant.components import remote, media_player

from .const import RemoteButton
from .mydevice import MyDevice

logger = logging.getLogger(__name__)

SERVICE_SEND_COMMAND = "send_command"

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

    async def send_remote_button(self, name):
        return await self._service(service="send_command", command=self.keymap[name])

    keymap = {
        RemoteButton.KEY_UP: "up",
        RemoteButton.KEY_DOWN: "down",
        RemoteButton.KEY_LEFT: "left",
        RemoteButton.KEY_RIGHT: "right",
        RemoteButton.KEY_EXIT: "home",
        RemoteButton.KEY_OK: "select",
        RemoteButton.KEY_PLAY: "play",
        RemoteButton.KEY_PAUSE: "play",
        RemoteButton.KEY_MENU: "back",
        RemoteButton.KEY_REWIND: "reverse",
        RemoteButton.KEY_FORWARD: "forward",
    }


class RokuSources:
    denon = "AV\xa0receiver"
    home = "Home"
    pandora = "Pandora"
    pbs = "PBS"
    plex = "Plex - Stream for Free"
    prime = "Prime Video"
    qvc = "QVC & HSN"
    youtube = "YouTube"


class Roku(MyDevice):
    domain = media_player.DOMAIN
    entity_id = f"{domain}.55_tcl_roku_tv"
    on_states = ["home", "on"]
    off_states = ["standby", "off"]
    sources = RokuSources()

    def __init__(self, hass):
        super().__init__(hass)
        self.remote = RokuRemote(hass)

    def is_on(self):
        return self.state.state not in self.off_states

    @property
    def supported_keys(self):
        return self.remote.supported_keys

    async def send_remote_button(self, name):
        return await self.remote.send_remote_button(name)

    async def set_source(self, source):
        # If it's not on, it needs to be
        logger.warning(f"ROKU SET SOURCE {source}")
        # if source not in self.state.attributes["source_list"]:
        #     logger.error(f"ROKU: source {source!r} is not valid. Choices are {self.state.attributes['source_list']!r}")
        #     return
        if not self.is_on():
            await self.turn_on()
            await asyncio.sleep(0.3)
        await self._service(service="select_source", source=source)
