import logging
from pprint import pformat
from typing import Optional

from homeassistant.const import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import State
from homeassistant.helpers.entity import Entity

logger = logging.getLogger(__name__)


class MyDevice:
    """
    Parent class for controlling my devices.
    Common code for handy things.
    """
    domain = None
    entity_id = None
    on_states = []
    keymap = {}

    def __init__(self, hass):
        self.hass = hass

    @property
    def supported_keys(self):
        return self.keymap.keys()

    def send_remote_button(self, name):
        raise NotImplementedError

    def get_entity_object(self) -> Entity:
        # Try not to use this, or at least just to explore things.
        pass

    @property
    def current_source(self) -> str:
        return self.state.attributes.get("source")

    @property
    def volume_level(self):
        state = self.state
        attrs = state.attributes
        if "volume_level" in attrs:
            # logger.warning(f'volume level of {self.entity_id} = {state["attributes"]["volume_level"]}')
            return attrs["volume_level"]

    @property
    def state(self) -> State:
        state = self.hass.states.get(self.entity_id)
        # logger.warning(f"\n===\nstate of {self.entity_id} = {pformat(state.state)}\n===")
        # logger.warning(f"state of {self.entity_id} = {pformat(state.as_dict())}")
        return state

    def is_on(self):
        return self.state.state in self.on_states

    async def _service(self, service:str, domain:Optional[str]=None, **moredata):
        """
        Submit a service request to this devices' entity.
        """
        if domain is None:
            domain = self.domain
        logger.warning(f"_service({service}, {domain}, {self.entity_id}, {moredata}")
        return await self.hass.services.async_call(  # coroutine
            domain=domain,
            service=service,
            service_data=dict(entity_id=self.entity_id, **moredata),
        )

    async def turn_off(self):
        """
        Turn off the device.
        """
        if self.is_on():
            logger.warning(f"Turning off {self.entity_id}: state={self.state.state}")
            return await self._service(SERVICE_TURN_OFF)
        else:
            logger.warning(f"Not turning off {self.entity_id} it does not appear to be on state={self.state.state}")

    async def turn_on(self):
        """
        Turn on the device.
        """
        if not self.is_on():
            logger.warning(f"Turning on {self.entity_id}: state={self.state.state}")
            return await self._service(SERVICE_TURN_ON)
        else:
            logger.warning(f"Not turning on {self.entity_id} it does not appear to be off state={self.state.state}")
