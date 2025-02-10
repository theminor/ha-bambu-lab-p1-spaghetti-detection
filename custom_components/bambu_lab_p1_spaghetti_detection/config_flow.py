from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import selector

from custom_components.bambu_lab_p1_spaghetti_detection import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            self.device_type = user_input["device_type"]
            return await self.async_step_select_device()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("device_type", description="Device Type"): vol.In(["Bambu Lab", "Moonraker"]),
            })
        )

    async def async_step_select_device(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            user_input["device_type"] = self.device_type
            return self.async_create_entry(title="Bambu Lab P1 - Spaghetti Detection", data=user_input)

        # Set the integration_type before showing the form
        if self.device_type == "Bambu Lab":
            integration_type = "bambu_lab"
        else:
            integration_type = "moonraker"

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema({
                vol.Required("camera_entity", description="Camera Entity"): selector({"entity": {"domain": "camera"}}),
                vol.Optional("update_interval", default=5, description="Update Interval (seconds)"): vol.All(vol.Coerce(int), vol.Range(min=2)),
                vol.Optional("obico_ml_api_host", default="http://127.0.0.1:3333", description="Obico Addon Host address (including port)"): str,
                vol.Optional("obico_ml_api_token", default="obico_api_secret", description="Obico Addon API Token"): str,
                vol.Required("printer_device", description="Printer to Monitor"): selector({"device": {"integration": integration_type}}),
            })
        )