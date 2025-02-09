import logging
import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.helpers.entity_component import async_update_entity

DOMAIN = "bambu_lab_p1_spaghetti_detection"
BRAND = "Bambu Lab P1 - Spaghetti Detection"

LOGGER = logging.getLogger(__package__)

PLATFORMS = [Platform.NUMBER, Platform.DATETIME, Platform.CAMERA]

SPAGHETTI_DETECTION_SCHEMA = vol.Schema({
    vol.Required("obico_host"): str,
    vol.Required("obico_auth_token"): str,
    vol.Required("image_url"): str,
})

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Bambu Lab P1 - Spaghetti Detection integration."""
    camera_entity_id = entry.data["camera_entity"]
    hass.data[DOMAIN] = {"camera_entity_id": camera_entity_id}

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
                image_data = await response.read()
                result = await response.json()

        # Update the camera entity with the image data
        camera_entity = hass.data[DOMAIN]["camera"]
        camera_entity.update_image(image_data)
        await async_update_entity(hass, "camera.spaghetti_detection_camera")

        return {"result": result}

    hass.services.async_register(
        DOMAIN,
        "predict",
        spaghetti_detection_handler,
        schema=SPAGHETTI_DETECTION_SCHEMA,
        supports_response=SupportsResponse.ONLY
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Bambu Lab P1 - Spaghetti Detection integration."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)