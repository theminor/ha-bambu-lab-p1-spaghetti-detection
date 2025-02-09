from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta
import aiohttp
import logging

DOMAIN = "bambu_lab_p1_spaghetti_detection"
BRAND = "Bambu Lab P1 - Spaghetti Detection"

LOGGER = logging.getLogger(__package__)

PLATFORMS = [Platform.NUMBER, Platform.DATETIME, Platform.CAMERA, Platform.SWITCH, Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Bambu Lab P1 - Spaghetti Detection integration."""
    camera_entity_id = entry.data["camera_entity"]
    update_interval = entry.data.get("update_interval", 60)
    obico_ml_api_host = entry.data.get("obico_ml_api_host", "http://127.0.0.1:3333")
    obico_ml_api_token = entry.data.get("obico_ml_api_token", "obico_api_secret")
    printer_device = entry.data["printer_device"]

    # Initialize the domain data dictionary
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    async def spaghetti_detection_handler(now):
        if not hass.data[DOMAIN]["active"]:
            return

        # Get the image from the camera entity
        camera = hass.data[DOMAIN]["camera"]
        image = await camera.async_camera_image()

        # Make the API call to the Obico ML server
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{obico_ml_api_host}/p", json={"image": image, "token": obico_ml_api_token}) as response:
                if response.status != 200:
                    LOGGER.error("Failed to get response from Obico ML server")
                    return

                result = await response.json()

                # Placeholder for applying logic to the result
                # Update the entities based on the result
                # Example:
                # hass.states.async_set("sensor.adjusted_ewm_mean", result["adjusted_ewm_mean"])
                # hass.states.async_set("sensor.thresh_warning", result["thresh_warning"])
                # hass.states.async_set("sensor.thresh_failure", result["thresh_failure"])
                # hass.states.async_set("switch.spaghetti_detection_active", result["spaghetti_detection_switch"])
                # hass.states.async_set("sensor.failure_detection_result", result["failure_detection_result"])

    # Track the time interval for the spaghetti detection handler
    hass.data[DOMAIN]["active"] = False
    hass.data[DOMAIN]["camera_entity_id"] = camera_entity_id
    hass.data[DOMAIN]["camera"] = None
    hass.data[DOMAIN]["update_interval"] = async_track_time_interval(hass, spaghetti_detection_handler, timedelta(seconds=update_interval))

    # Load platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the Bambu Lab P1 - Spaghetti Detection integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN]["update_interval"]()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok