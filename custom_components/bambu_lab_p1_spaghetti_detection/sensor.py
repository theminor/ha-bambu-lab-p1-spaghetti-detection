from homeassistant.components.sensor import SensorEntity
from . import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    sensor = FailureDetectionSensor(hass, "Failure Detection Result", entry.entry_id)
    async_add_entities([sensor])

class FailureDetectionSensor(SensorEntity):
    def __init__(self, hass, name, entry_id):
        self.hass = hass
        self._name = name
        self._entry_id = entry_id
        self._state = "None"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return f"{self._entry_id}_failure_detection_result"

    def update_state(self, new_state):
        self._state = new_state
        self.async_write_ha_state()