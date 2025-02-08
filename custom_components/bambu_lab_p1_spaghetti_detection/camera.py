from homeassistant.components.camera import Camera
from . import DOMAIN  # Import DOMAIN from the __init__.py file

async def async_setup_entry(hass, entry, async_add_entities):
    camera = SpaghettiDetectionCamera(hass, "Spaghetti Detection Camera", entry.entry_id)
    hass.data[DOMAIN] = {"camera": camera}
    async_add_entities([camera])

class SpaghettiDetectionCamera(Camera):
    def __init__(self, hass, name, entry_id):
        super().__init__()
        self.hass = hass
        self._name = name
        self._entry_id = entry_id
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
        return self._image_data

    def update_image(self, image_data):
        self._image_data = image_data

    async def async_update(self):
        # No need to update anything here
        pass