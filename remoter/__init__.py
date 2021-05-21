import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant, callback

from .const import RemoteButton, DOMAIN
from .debouncer import Debouncer
from .denon import Denon
from .firestick import FireStick, FireStickSources

# from .moth import Moth
from .roku import Roku, RokuSources

logger = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = []

# Some remote buttons start "scenes" (not home assistant's scenes, but the same idea)
ROKU_SCENES = {
    # Scenes which involve setting a source/app on Roku, and not using Firestick at all
    RemoteButton.KEY_RED: RokuSources.home,
    RemoteButton.KEY_BLUE: RokuSources.qvc,  # also available on Firestick
    RemoteButton.KEY_YELLOW: RokuSources.hbo_max,
    RemoteButton.KEY_1: RokuSources.plex,
    RemoteButton.KEY_2: RokuSources.youtube,
    RemoteButton.KEY_3: RokuSources.pandora,
    RemoteButton.KEY_4: RokuSources.pbs,
    RemoteButton.KEY_5: RokuSources.prime,  # also available on Firestick
}

FIRESTICK_SCENES = {
    # Scenes which involve a source/app on firestick
    RemoteButton.KEY_GREEN: FireStickSources.home,
    # RemoteButton.KEY_YELLOW: FireStickSources.hbomax,
    RemoteButton.KEY_6: FireStickSources.jellyfin,
    # RemoteButton.KEY_7: FireStickSources.prime,  # also available on Roku
    # RemoteButton.KEY_8: FireStickSources.qvc,  # also available on Roku
}


async def async_setup(hass: HomeAssistant, config: dict):
    logger.warning("remoter: setup")

    futures_pending = []
    next_task_id = 1

    def remember_future(f):
        nonlocal next_task_id
        if f is None:
            return
        id = next_task_id
        next_task_id += 1
        futures_pending.append({"id": id, "future": f})
        logger.warning(f"Task {id} started")

    # Check for finished futures
    def check_tasks():
        for fp in list(futures_pending):
            f = fp["future"]
            id = fp["id"]
            if f.done():
                futures_pending.remove(fp)
                e = f.exception()
                if e:
                    logger.error(f"remoter: future {id} had exception: {e}")
            #     else:
            #         logger.warning(f"task {id} completed successfully")
            # else:
            #     logger.warning(f"task {id} not done yet")

    def start(*targets):
        """
        targets should be coroutine objects, possibly other awaitables.
        This schedules them to be run by homeassistant, without
        blocking this thread to wait for them.

        We need to run things this way because we're driven by an event
        handler which should not block.
        """
        for target in targets:
            if target:  # Could be None
                remember_future(hass.async_add_job(target))

    debouncer = Debouncer()
    denon = Denon(hass)
    firestick = FireStick(hass)
    roku = Roku(hass)
    # moth = Moth(hass)

    def watch_on_roku(source):
        # Schedules itself
        logger.warning(f"watch on roku: {source}")
        start(
            roku.set_source(source),
            denon.set_source(denon.sources.roku),
            firestick.turn_off(),
        )

    def watch_on_firestick(source):
        # Schedules itself
        logger.warning(f"watch on firestick: {source}")
        start(
            roku.set_source(roku.sources.denon),
            denon.set_source(denon.sources.firestick),
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
        name = event.data.get("button_name")
        logger.warning(f"button={name}")
        check_tasks()

        # Slow things down - except for a few keys we want to repeat
        if name not in RemoteButton.REPEATABLE_KEYS and debouncer.debounce(event):
            return

        # What's the mode? Depending on what we're watching, we want to route some
        # button pushes differently. E.g. if we're watching something on the firestick,
        # play, pause, up, down, etc should be sent to the firestick. If not, we should
        # send them to the Roku.
        mode = denon.get_mode()

        if mode == "roku":
            logger.warning(f"roku source = {roku.current_source}")

        if name == RemoteButton.KEY_POWER:
            # SHUT IT ALL DOWN
            start(
                denon.turn_off(),
                roku.turn_off(),
                firestick.turn_off(),
            )

        elif name == RemoteButton.KEY_9:
            # Junebug?
            start(
                denon.set_source(denon.sources.junebug),
                roku.set_source(roku.sources.denon),
            )

        # elif name == RemoteButton.KEY_9:
        #     start(
        #         denon.set_source(denon.sources.moth),
        #         roku.set_source(roku.sources.denon),
        #         firestick.turn_off(),
        #     )

        elif name in ROKU_SCENES:
            watch_on_roku(ROKU_SCENES[name])
        elif name in FIRESTICK_SCENES:
            watch_on_firestick(FIRESTICK_SCENES[name])

        # DEVICE and MODE SPECIFIC: control whatever's running
        elif name in denon.supported_keys:  # mainly volume controls
            logger.warning(denon.volume_level)
            start(denon.send_remote_button(name))
        # elif mode == "moth" and name in moth.supported_keys:
        #     start(moth.send_remote_button(name))
        elif mode == "roku" and name in roku.supported_keys:  # navigate in Roku
            start(roku.send_remote_button(name))
        elif (
            mode == "firestick" and name in firestick.supported_keys
        ):  # navigate in firestick
            start(firestick.send_remote_button(name))

        else:
            logger.error(f"Unrecognized remote key {name}")

    hass.bus.async_listen("ir_command_received", handle_event)
    logger.warning(
        "\n*******************\nremoter: setup complete\n*******************"
    )
    return True
