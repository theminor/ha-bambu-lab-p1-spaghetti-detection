from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta
import aiohttp
import logging
import base64

DOMAIN = "bambu_lab_p1_spaghetti_detection"
BRAND = "Bambu Lab P1 - Spaghetti Detection"

LOGGER = logging.getLogger(__package__)

PLATFORMS = [Platform.NUMBER, Platform.DATETIME, Platform.CAMERA, Platform.SWITCH, Platform.SENSOR]

THRESHOLD_LOW = 0.38
THRESHOLD_HIGH = 0.78

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

    # Initialize variables
    ewm_mean = 0
    rolling_mean_short = 0
    rolling_mean_long = 0
    current_frame_number = 0
    lifetime_frame_number = 0

    async def spaghetti_detection_handler(now):
        nonlocal ewm_mean, rolling_mean_short, rolling_mean_long, current_frame_number, lifetime_frame_number

        if not hass.data[DOMAIN]["active"]:
            return

        # Get the image from the camera entity
        camera = hass.data[DOMAIN]["camera"]
        try:
            image = await camera.async_camera_image()
        except Exception as e:
            LOGGER.error("Failed to get image from camera: %s", e)
            return

        # Encode the image to base64
        try:
            image_base64 = base64.b64encode(image).decode('utf-8')
        except Exception as e:
            LOGGER.error("Failed to encode image to base64: %s", e)
            return

        # Prepare the payload for the POST request
        payload = {
            "img": image_base64,
            "threshold": 0.08,
            "rectangleColor": [0, 0, 255],
            "rectangleThickness": 5,
            "fontFace": "FONT_HERSHEY_SIMPLEX",
            "fontScale": 1.5,
            "textColor": [0, 0, 255],
            "textThickness": 2
        }

        # Make the API call to the Obico ML server
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{obico_ml_api_host}/detect/", json=payload, headers={"Authorization": f"Bearer {obico_ml_api_token}"}) as response:
                    if response.status != 200:
                        LOGGER.error("Failed to get response from Obico ML server, status code: %s", response.status)
                        return

                    result = await response.json()
            except aiohttp.ClientError as e:
                LOGGER.error("HTTP request to Obico ML server failed: %s", e)
                return
            except Exception as e:
                LOGGER.error("Failed to process response from Obico ML server: %s", e)
                return

            # Process the result
            p_sum = sum(detection[1] for detection in result["detections"])
            current_frame_number += 1
            lifetime_frame_number += 1

            ewm_mean = (p_sum * 2 / (12 + 1)) + (ewm_mean * (1 - 2 / (12 + 1)))
            rolling_mean_short = rolling_mean_short + ((p_sum - rolling_mean_short) / (310 if 310 <= current_frame_number else current_frame_number + 1))
            rolling_mean_long = rolling_mean_long + ((p_sum - rolling_mean_long) / (7200 if 7200 <= lifetime_frame_number else lifetime_frame_number + 1))

            adjusted_ewm_mean = 0  # Initialize adjusted_ewm_mean
            thresh_warning = 0  # Initialize thresh_warning
            thresh_failure = 0  # Initialize thresh_failure
            normalized_p = 0  # Initialize normalized_p

            if current_frame_number >= 3:   # Do not begin detection until we have at least 30 frames # *** CHANGE BACK TO 30 after testing ***

                adjusted_ewm_mean = ewm_mean - rolling_mean_long
                rolling_mean_diff = (rolling_mean_short - rolling_mean_long) * 3.8
                thresh_warning = min(0.78, max(0.33, rolling_mean_diff))
                thresh_failure = thresh_warning * 1.75
                p = min(1, max(2/3, (adjusted_ewm_mean - rolling_mean_diff) / (thresh_failure * 1.5 - thresh_failure) + 2/3))

                if p > thresh_failure:
                    normalized_p = min(1, max(2/3, ((p - thresh_failure) * (1 - 2/3)) / (thresh_failure * 1.5 - thresh_failure) + 2/3))
                elif p > thresh_warning:
                    normalized_p = min(2/3, max(1/3, ((p - thresh_warning) * (2/3 - 1/3)) / (thresh_failure - thresh_warning) + 1/3))
                else:
                    normalized_p = min(1/3, max(0, (p * 1/3) / thresh_warning))

                if adjusted_ewm_mean < THRESHOLD_LOW:
                    hass.states.async_set("sensor.failure_detection_result", "OK")
                elif (adjusted_ewm_mean <= THRESHOLD_HIGH) and (adjusted_ewm_mean <= rolling_mean_diff):
                    hass.states.async_set("sensor.failure_detection_result", "Warning")
                    # "Confidence: {{ (states('number.bambu_lab_p1_spaghetti_detection_normalized_p') | float * 100) | int }}%"
                else:
                    hass.states.async_set("sensor.failure_detection_result", "Failure")
                    # "Confidence: {{ (states('number.bambu_lab_p1_spaghetti_detection_normalized_p') | float * 100) | int }}%"

            # Update the entities based on the result
            hass.states.async_set("sensor.adjusted_ewm_mean", adjusted_ewm_mean)
            hass.states.async_set("sensor.thresh_warning", thresh_warning)
            hass.states.async_set("sensor.thresh_failure", thresh_failure)
            hass.states.async_set("sensor.normalized_p", normalized_p)
            # hass.states.async_set("switch.spaghetti_detection_active", hass.data[DOMAIN]["active"])
            # hass.states.async_set("sensor.failure_detection_result", result["detections"])

            # Optionally, handle the image with detections
            #image_with_detections = result.get("image_with_detections")
            #if image_with_detections:
            #    hass.states.async_set("sensor.image_with_detections", image_with_detections)

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