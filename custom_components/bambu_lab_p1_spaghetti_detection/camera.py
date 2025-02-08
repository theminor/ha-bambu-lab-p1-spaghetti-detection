from homeassistant.components.camera import Camera
from . import DOMAIN  # Import DOMAIN from the __init__.py file

async def async_setup_entry(hass, entry, async_add_entities):
    camera = SpaghettiDetectionCamera(hass, "Spaghetti Detection Camera")
    hass.data[DOMAIN] = {"camera": camera}
    async_add_entities([camera])

class SpaghettiDetectionCamera(Camera):
    def __init__(self, hass, name):
        super().__init__()
        self.hass = hass
        self._name = name
        self._image_data = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return "idle"

    async def async_camera_image(self):
        return self._image_data

    def update_image(self, image_data):
        self._image_data = image_data

    async def async_update(self):
        # No need to update anything here
        pass