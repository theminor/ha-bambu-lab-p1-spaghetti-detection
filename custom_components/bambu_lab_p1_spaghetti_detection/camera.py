from homeassistant.components.camera import Camera, async_get_image
from . import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    camera_entity_id = hass.data[DOMAIN]["camera_entity_id"]
    camera = SpaghettiDetectionCamera(hass, "Spaghetti Detection Camera", entry.entry_id, camera_entity_id)
    hass.data[DOMAIN]["camera"] = camera
    async_add_entities([camera])

class SpaghettiDetectionCamera(Camera):
    def __init__(self, hass, name, entry_id, camera_entity_id):
        super().__init__()
        self.hass = hass
        self._name = name
        self._entry_id = entry_id
        self._camera_entity_id = camera_entity_id
        self._image_data = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return "idle"

    @property
    def unique_id(self):
        return f"{self._entry_id}_spaghetti_detection_camera"

    async def async_camera_image(self):
        if self._image_data:
            return self._image_data

        # Fetch the image from the selected camera entity
        image = await async_get_image(self.hass, self._camera_entity_id)
        return image.content

    def update_image(self, image_data):
        self._image_data = image_data

    async def async_update(self):
        # No need to update anything here
        pass