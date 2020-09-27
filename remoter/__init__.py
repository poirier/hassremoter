import asyncio
import logging
from pprint import pformat

import voluptuous as vol

from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON,
    STATE_OFF,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback

from .const import REPEATABLE_KEYS, UNREPEATABLE_KEYS, RemoteButton, DOMAIN
from .debouncer import Debouncer
from .denon import Denon
from .firestick import FireStick
from .roku import Roku

logger = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = []


async def async_setup(hass: HomeAssistant, config: dict):
    logger.warning("remoter: setup")

    def do(*targets):
        """
        targets should be coroutine objects, possibly other awaitables.
        This schedules them to be run by homeassistant, without
        blocking this thread to wait for them.

        We need to run things this way because we're driven by an event
        handler which should not block.
        """
        for target in targets:
            if target:  # Could be None
                hass.async_add_job(target)

    def start_scene(entity_id):
        do(
            hass.services.async_call(
                domain="scene",
                service="turn_on",
                service_data={ATTR_ENTITY_ID: entity_id},
            )
        )

    debouncer = Debouncer()
    denon = Denon(hass)
    firestick = FireStick(hass)
    roku = Roku(hass)

    def watch_on_roku(source):
        # Schedules itself
        do(
            roku.set_source(source),
            denon.set_source("Opt1 TV Aud"),
            firestick.turn_off(),
        )

    def watch_on_firestick(source):
        # Schedules itself
        do(
            roku.set_source("AV\xa0receiver"),
            denon.set_source("3Bluray/Fire"),
            firestick.set_source(source),
        )

    # foo = False

    """
    keys in hass.data:
    ['aiohttp_clientsession', 'aiohttp_connector', 'androidtv', 'area_registry', 'astral_location_cache', 'auth', 
    'auth_mfa_setup_flow_manager', 'automation', 'binary_sensor', 'cast', 'cast_added_cast_devices', 
    'cast_discovery_running', 'cast_known_chromecasts', 'cast_multizone_manager', 'climate', 'cloud', 
    'cloud_account_link_services', 'components', 'core.uuid', 'cover', 'custom_components', 'denonavr', 
    'deps_reqs_processed', 'device_registry', 'device_tracker', 'dispatcher', 'entity_components', 
    'entity_info', 'entity_platform', 'entity_registry', 'fan', 'frontend_default_theme', 'frontend_extra_js_url_es5', 
    'frontend_extra_module_url', 'frontend_panels', 'frontend_storage', 'frontend_themes', 'frontend_themes_store', 
    'group', 'group_order', 'hass_customize', 'helpers.script', 'history_bakery', 'homeassistant_scene', 'image', 
    'integrations', 'integrations_with_reqs', 'ios', 'ipp', 'light', 'lock', 'logbook', 'logging', 'lovelace', 
    'media_player', 'media_source', 'mfa_auth_module_reqs_processed', 'mobile_app', 'mqtt', 'mqtt_config', 
    'mqtt_config_entry_is_setup', 'mqtt_config_entry_lock', 'mqtt_debug_info', 'mqtt_discovered_components', 
    'mqtt_discovery_unsubscribe', 'mqtt_last_discovery', 'notify_services', 'oauth2_impl', 'oauth2_providers', 
    'persistent_notification', 'person', 'pip_lock', 'recorder_instance', 'remote', 'restore_state_task', 'roku', 
    'scene', 'script', 'sensor', 'setup_done', 'setup_started', 'setup_tasks', 'sonos', 'sonos_media_player', 
    'switch', 'system_health', 'tag', 'template.environment', 'track_entity_registry_updated_callbacks', 
    'track_entity_registry_updated_listener', 'track_state_change_callbacks', 'track_state_change_listener', 
    'updater', 'webhook', 'websocket_api', 'wemo', 'zeroconf', 'zha', 'zha_storage', 'zone']
    """

    # Listener to handle fired events
    @callback
    def handle_event(event):
        # nonlocal foo
        #
        # if not foo:
        #     #logger.warning(f"Keys in data: {sorted(list(hass.data.keys()))}")
        #     logger.warning(pformat(hass.data["androidtv"]))
        #
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
        #
        #     foo = True



        name = event.data.get("button_name")
        logger.warning(f"button={name}")
        # Slow things down - except for a few keys we want to repeat
        if name not in REPEATABLE_KEYS and debouncer.debounce(event):
            return

        mode = None
        firestick_state = firestick.state
        logger.warning(
            "Firestick: state=%s, attributes=%s",
            firestick_state.state,
            firestick_state.attributes,
        )
        roku_state = roku.state
        logger.warning(
            "Roku: state=%s, attributes=%s", roku_state.state, roku_state.attributes
        )
        st = denon.state
        logger.warning("Denon: state=%s, attributes=%s", st.state, st.attributes)
        roku_remote_state = roku.remote.state
        logger.warning(
            "Roku remote: state=%s, attributes=%s",
            roku_remote_state.state,
            roku_remote_state.attributes,
        )

        # What's the mode? Depending on what we're watching, we want to route some
        # button pushes differently. E.g. if we're watching something on the firestick,
        # play, pause, up, down, etc should be sent to the firestick. If not, we should
        # send them to the Roku.
        mode = None
        source = denon.current_source
        if source == "3Bluray/Fire":
            mode = "firestick"
        elif source == "Opt1 TV Aud":
            mode = "roku"
        elif source == "2 DVD/Chrome":
            mode = "chromecast"

        if name == RemoteButton.KEY_POWER:
            # SHUT IT ALL DOWN
            do(
                denon.turn_off(), roku.turn_off(), firestick.turn_off(),
            )
            logger.warning("exit modes")
        elif name == RemoteButton.KEY_RED:
            watch_on_roku("Home")
        elif name == RemoteButton.KEY_GREEN:
            # WATCH FIRESTICK
            # start_scene("scene.harmony_firestick")  # FIXME: do this ourselves
            watch_on_firestick("com.amazon.tv.launcher")
            logger.warning("enter firestick mode")
        elif name == RemoteButton.KEY_YELLOW:
            # WATCH CHROMECAST
            start_scene("scene.hamony_chromecast")  # FIXME: do this ourselves
            logger.warning("start chromecast scene")
            do(firestick.turn_off())
        elif name == RemoteButton.KEY_BLUE:
            watch_on_roku("QVC & HSN")
        elif name == RemoteButton.KEY_1:
            watch_on_roku("Plex - Stream for Free")
        elif name == RemoteButton.KEY_2:
            watch_on_roku("YouTube")
        elif name == RemoteButton.KEY_3:
            watch_on_roku("Pandora")
        elif name == RemoteButton.KEY_4:
            watch_on_roku("PBS")
        elif name == RemoteButton.KEY_5:
            watch_on_roku("Prime Video")
        elif name == RemoteButton.KEY_6:
            watch_on_firestick("Jellyfin")
        elif name == RemoteButton.KEY_7:
            watch_on_firestick("Amazon Video")
        elif name == RemoteButton.KEY_8:  # QVC/Firestick
            watch_on_firestick("com.qvc.firetv")
        elif name in denon.supported_keys:
            # These are mostly the volume keys, which we always send to the receiver.
            do(denon.send_key(name))
        elif mode == "roku" and name in roku.supported_keys:
            do(roku.send_key(name))
        elif name == RemoteButton.KEY_RECORD:
            # Press RECORD, then within  a few seconds press a button on the real
            # firetv remote. Within 10 seconds, a notification should appear in homeassistant
            # containing a string of 'sendevent' commands that can be used to more quickly
            # have the same effect as that firestick remote button.
            do(firestick.learn_sendevent())
            logger.warning(
                "RECORDING for a few seconds... press ONE BUTTON on the REAL Firetv remote"
            )
        elif name in firestick.supported_keys:
            do(firestick.send_key(name))
        else:
            logger.error(f"Unrecognized remote key {name}")

    hass.bus.async_listen("ir_command_received", handle_event)
    logger.warning(
        "\n*******************\nremoter: setup complete\n*******************"
    )
    return True
