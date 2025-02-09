import logging
import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

DOMAIN = "bambu_lab_p1_spaghetti_detection"
BRAND = "Bambu Lab P1 - Spaghetti Detection"

LOGGER = logging.getLogger(__package__)

PLATFORMS = [Platform.NUMBER, Platform.DATETIME, Platform.CAMERA, Platform.SWITCH, Platform.SENSOR]

SPAGHETTI_DETECTION_SCHEMA = vol.Schema({
    vol.Required("obico_host"): str,
    vol.Required("obico_auth_token"): str,
    vol.Required("image_url"): str,
})

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Bambu Lab P1 - Spaghetti Detection integration."""
    camera_entity_id = entry.data["camera_entity"]
    update_interval = entry.data.get("update_interval", 60)
    obico_ml_api_host = entry.data.get("obico_ml_api_host", "http://127.0.0.1:3333")
    obico_ml_api_token = entry.data.get("obico_ml_api_token", "obico_api_secret")
    printer_device = entry.data["printer_device"]
    hass.data[DOMAIN] = {"camera_entity_id": camera_entity_id, "update_interval": update_interval, "active": False}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def spaghetti_detection_handler(call: ServiceCall) -> ServiceResponse:
        """Handle the custom service."""
        obico_host = call.data.get("obico_host", "")
        obico_auth_token = call.data.get("obico_auth_token", "")
        image_url = call.data.get("image_url", "")

        if obico_host.endswith("/"):
            obico_host = obico_host[:-1]

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{obico_host}/p/?img={image_url}",
                                   headers={"Authorization": f"Bearer {obico_auth_token}"}) as response:
                result = await response.json()

        # Update the camera entity with the full result
        camera = hass.data[DOMAIN].get("camera")
        if camera:
            camera.update_detection_result(result)

        # Update the failure detection sensor state
        sensor = hass.data[DOMAIN].get("failure_detection_sensor")
        if sensor:
            detection_result = result.get("result", {}).get("detection_result", "None")
            sensor.update_state(detection_result)

        return {"result": result}

    async def periodic_spaghetti_detection(now):
        if hass.data[DOMAIN]["active"]:
            await spaghetti_detection_handler(ServiceCall(DOMAIN, "predict", entry.data))

    hass.services.async_register(
        DOMAIN,
        "predict",
        spaghetti_detection_handler,
        schema=SPAGHETTI_DETECTION_SCHEMA,
        supports_response=SupportsResponse.ONLY
    )

    async_track_time_interval(hass, periodic_spaghetti_detection, timedelta(seconds=update_interval))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Bambu Lab P1 - Spaghetti Detection integration."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)