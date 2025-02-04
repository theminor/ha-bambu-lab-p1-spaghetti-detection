from datetime import datetime, timezone

from homeassistant.components.datetime import DateTimeEntity, DateTimeEntityDescription

DATETIME_TYPES: tuple[DateTimeEntityDescription, ...] = (
    DateTimeEntityDescription(
        key="last_notify_time",
        name="Spaghetti Detection - Last Notify Time"
    ),
)

async def async_setup_entry(hass, entry, async_add_entities):
    entities = [
        BambuLabP1SpaghettiDetectionDateTimeEntity(entity_description, entry.title) for entity_description in DATETIME_TYPES
    ]

    async_add_entities(entities)

class BambuLabP1SpaghettiDetectionDateTimeEntity(DateTimeEntity):
    def __init__(self, entity_description, entry_title):
        self.entity_description = entity_description

        self.entity_id = f"datetime.bambu_lab_p1_spaghetti_detection_{entry_title}_{entity_description.key}"
        self._attr_unique_id = f"datetime.bambu_lab_p1_spaghetti_detection_{entry_title}_{entity_description.key}"
        self._attr_native_value = datetime.fromtimestamp(0, timezone.utc)

    async def async_set_value(self, value: datetime) -> None:
        """Set the value of the number entity."""
        self._attr_native_value = value
        self.async_write_ha_state()

    async def set_value(self, value: datetime) -> None:
        """Set the value of the number entity."""
        self._attr_native_value = value
        self.async_write_ha_state()
