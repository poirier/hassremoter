import logging
from pprint import pformat

from homeassistant.const import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import State

logger = logging.getLogger(__name__)


class MyDevice:
    """
    Parent class for controlling my devices.
    Common code for handy things.
    """
    domain = None
    entity_id = None
    on_states = []

    def __init__(self, hass):
        self.hass = hass

    @property
    def current_source(self) -> str:
        return self.state.attributes.get("source")

    @property
    def state(self) -> State:
        state = self.hass.states.get(self.entity_id)
        logger.warning(f"\n===\nstate of {self.entity_id} = {pformat(state.state)}\n===")
        # logger.warning(f"state of {self.entity_id} = {pformat(state.as_dict())}")
        return state

    def is_on(self):
        return self.state.state in self.on_states

    async def _service(self, service, **moredata):
        """
        Submit a service request to this devices' entity.
        """
        return await self.hass.services.async_call(  # coroutine
            domain=self.domain,
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
