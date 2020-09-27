from homeassistant.components.media_player.const import SERVICE_SELECT_SOURCE
from homeassistant.const import (
    CONF_SOURCE,
    SERVICE_VOLUME_UP,
    SERVICE_VOLUME_DOWN,
    SERVICE_VOLUME_MUTE,
)

from .const import RemoteButton
from .mydevice import MyDevice


class Denon(MyDevice):
    """
    Control my Denon receiver, which handles audio as well as routing
    video from other devices to the Roku/TV.
    """
    domain = "media_player"
    entity_id = f"{domain}.denon"
    on_states = ["on"]

    @property
    def supported_keys(self):
        return DENON_REMOTE_BUTTON_TO_SERVICE.keys()

    async def set_source(self, source):
        """
        This tells the Denon which input to use.
        This also turns it on, so we don't really need a .turn_on method.
        """
        return await self._service(SERVICE_SELECT_SOURCE, **{CONF_SOURCE: source})

    async def send_key(self, name):
        return await self._service(DENON_REMOTE_BUTTON_TO_SERVICE[name])


DENON_REMOTE_BUTTON_TO_SERVICE = {
    RemoteButton.KEY_VOLUMEUP: SERVICE_VOLUME_UP,
    RemoteButton.KEY_VOLUMEDOWN: SERVICE_VOLUME_DOWN,
    RemoteButton.KEY_MUTE: SERVICE_VOLUME_MUTE,
}
