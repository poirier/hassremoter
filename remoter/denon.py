import logging

from homeassistant.components.media_player.const import SERVICE_SELECT_SOURCE
from homeassistant.const import (
    CONF_SOURCE,
    SERVICE_VOLUME_UP,
    SERVICE_VOLUME_DOWN,
    SERVICE_VOLUME_MUTE,
)

from .const import RemoteButton
from .mydevice import MyDevice


logger = logging.getLogger(__name__)


class DenonSources:
    # Names I understand mapped to the name of the source to actually set.
    firestick = "3Bluray/Fire"
    roku = "Opt1 TV Aud"


class Denon(MyDevice):
    """
    Control my Denon receiver, which handles audio as well as routing
    video from other devices to the Roku/TV.
    """
    domain = "media_player"
    entity_id = f"{domain}.denon"
    on_states = ["on"]
    sources = DenonSources()

    def get_mode(self):
        # What's the mode? Depending on what we're watching, we want to route some
        # button pushes differently. E.g. if we're watching something on the firestick,
        # play, pause, up, down, etc should be sent to the firestick. If not, we should
        # send them to the Roku.
        mode = None
        if not self.is_on():
            return "off"
        source = self.current_source
        if source == self.sources.firestick:
            mode = "firestick"
        elif source == self.sources.roku:
            mode = "roku"
        logger.warning("MODE = %s", mode)
        return mode

    async def set_source(self, source):
        """
        This tells the Denon which input to use.
        This also turns it on, so we don't really need a .turn_on method.
        """
        return await self._service(SERVICE_SELECT_SOURCE, **{CONF_SOURCE: source})

    async def send_remote_button(self, name):
        if name == RemoteButton.KEY_MUTE:
            return await self._service(service="volume_mute", is_volume_muted=True)
        elif name == RemoteButton.KEY_VOLUMEUP:
            return await self._service(service="volume_up")
        elif name == RemoteButton.KEY_VOLUMEDOWN:
            return await self._service(service="volume_down")
        return await self._service(self.keymap[name])


    keymap = {
        # Really we call specific services rather than sending button presses,
        # but these are the buttons we can handle.
        RemoteButton.KEY_VOLUMEUP: SERVICE_VOLUME_UP,
        RemoteButton.KEY_VOLUMEDOWN: SERVICE_VOLUME_DOWN,
        RemoteButton.KEY_MUTE: SERVICE_VOLUME_MUTE,
    }
