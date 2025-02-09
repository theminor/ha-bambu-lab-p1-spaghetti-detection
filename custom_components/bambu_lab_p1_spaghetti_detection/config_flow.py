from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import selector
from homeassistant.helpers import device_registry as dr

from custom_components.bambu_lab_p1_spaghetti_detection import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="Bambu Lab P1 - Spaghetti Detection", data=user_input)

        device_registry = dr.async_get(self.hass)
        devices = [
            (device.id, device.name) for device in device_registry.devices.values()
            if any(self.hass.config_entries.async_get_entry(entry_id).domain in ["bambu_lab", "moonraker"] for entry_id in device.config_entries)
        ]

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("camera_entity"): selector({"entity": {"domain": "camera"}}),
                vol.Optional("update_interval", default=60): vol.All(vol.Coerce(int), vol.Range(min=10)),
                vol.Optional("obico_ml_api_host", default="http://127.0.0.1:3333"): str,
                vol.Optional("obico_ml_api_token", default="obico_api_secret"): str,
                vol.Required("printer_device"): vol.In({device_id: device_name for device_id, device_name in devices}),
            })
        )