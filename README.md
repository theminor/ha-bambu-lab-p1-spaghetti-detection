# WORKING CHANGES - TO DO
- [ ] Test spaghetti detection
- [ ] Give each entity a unique id so that multiple integrations can be added
- [ ] Verify this is the pulled image and not our modified camera image with bounding boxes
- [ ] Verify printer is actually printing - check the print state shoudl be "running" or "printing" etc.
- [ ] Stop processing when printer stops and be sure to reset all the variables to 0
- [ ] Handle the camera and test detection boxes on the image


# Home Assistant Spaghetti Detection Integration

Upgrade your 3D printer experience with the Home Assistant Spaghetti Detection Integration. This
integration leverages the power of the [Bambu Lab Integration](https://github.com/greghesp/ha-bambulab), the [Moonraker Integration](https://github.com/denkyem/home-assistant-moonraker), and the [Obico](https://www.obico.io) ML server, providing a solution for detecting and handling spaghetti incidents during
your prints.

If you like this automation and would like to support it, you can [buy me a coffee](https://www.patreon.com/nberk/shop).

## Features

- **Spaghetti Detection:** Utilize Obico's machine learning server to identify and prevent spaghetti issues.
- **Critical/Standard Notifications:** Stay informed with customizable notifications.
- **Warn/Pause/Cancel Print on Failure Detection:** Take proactive measures by automatically warning, pausing or canceling print jobs upon the detection of spaghetti-related failures, preventing wasted material and time.
- **Third Party Camera Support:** Any camera entity can also be used for detecting failures.

## Supported Printers
| Device           | Compatibility | 
|------------------|---------------|
| X1 Series        | ✔️
| P1 Series        | ✔️
| A1 Series        | ✔️
| Klipper Printers | ✔️


## Prerequisites

Ensure the following prerequisites are met before installing the Spaghetti Detection Integration:

- [Bambu Lab Integration](https://github.com/greghesp/ha-bambulab) must be installed if you are using a Bambu printer.
- [Moonraker Integration](https://github.com/denkyem/home-assistant-moonraker) must be installed if you are using a Klipper printer.
- A server with at least 4GB of RAM that meets the [Obico hardware requirements](https://www.obico.io/docs/server-guides/hardware-requirements/).

<br>

> **_NOTE:_** The integration does **not** support the following devices:

| Device | Compatibility | 
| ------ | ------------- |
| Raspberry Pi (Any Model) | ❌
| Home Assistant Green | ❌
| Home Assistant Yellow | ❌
| Latte Panda | ❌
| Jetson Nano 2gb | ❌

## Setup

Follow these steps to set up the Spaghetti Detection Integration:

1. **Install Obico ML Server**
    - Choose between installing it as a Home Assistant Addon or as a standalone Docker container.

2. **Install `Spaghetti Detection` Home Assistant Integration**
3. **Install Home Assistant Spaghetti Detection Automation Blueprint**

For detailed installation instructions and troubleshooting tips, refer to
the [Installation Guide](#link-to-installation-guide).

## 1. Install Obico ML Server

### Install Obico ML Server as Home Assistant Addon

To install Obico ML server as a Home Assistant Add-on you have 2 options:

1. Click the **Add Add-On Repository** button below, click **Add → Close** (You might need to enter the **internal
   IP address** of your Home Assistant instance first).

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/nberktumer/ha-bambu-lab-p1-spaghetti-detection)

2. Add the repository URL under **Settings → Add-ons → ADD-ON STORE** and click **⋮ → Repositories**:

       https://github.com/nberktumer/ha-bambu-lab-p1-spaghetti-detection

### Install Obico ML Server as a Standalone Docker Container

1. Create docker container using the following command:

       docker create \
         --restart unless-stopped \
         --env ML_API_TOKEN=obico_api_secret \
         --publish 3333:3333 \
         --name ha_spaghetti_detection \
         nberk/ha_spaghetti_detection_standalone:latest

2. Start the container using the following command:

       docker start ha_spaghetti_detection

### Install Obico ML Server as a Standalone Docker Container with Docker Compose

1. Download the docker-compose.yaml from the repository

2. Edit the environment variables section in the docker compose yaml:

      ```
      environment:
        - ML_API_TOKEN=obico_api_secret
        - TZ=Europe/London
      ```

3. Run the command:

       docker compose up -d

## 2. Install Home Assistant Integration

### HACS

1. Click the button below to download and install the integration:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nberktumer&repository=ha-bambu-lab-p1-spaghetti-detection&category=Integration)

2. Go to **Settings → Devices & services → Add Integration** and add **Spaghetti Detection** integration.

### Manual

Manually copy the contents of the custom_components folder to your Home Assistant config/custom_components folder. After
restarting Home Assistant, add and configure the integration through the native integration setup.

## 3. Install Home Assistant Automation Blueprint

1. Click the button below to import the Spaghetti Detection blueprint:

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://github.com/nberktumer/ha-bambu-lab-p1-spaghetti-detection/blob/main/blueprints/spaghetti_detection.yaml)

2. Go to the imported blueprint and create the automation:

![Configure the automation](docs/images/blueprint_installation.png)

### Blueprint Parameters


| Parameter | Description |
| ---- | ----- |
| **Home Assistant Host** | The address of your Home Assistant instance. Required for sending the printer camera image to the Obico ML server. Ensure to include your Home Assistant port. This address is also used for notification images. If you wish to view failure images on notifications outside your local network, provide a publicly accessible link here.
| **Obico ML API Host** | The URL of the Obico ML Server. The default port number is `3333`. If you installed the ML server via the Home Assistant Addon, the IP address should match your Home Assistant address.
| **Obico ML API Auth Token** | The authentication token for the Obico ML Server. The default value is `obico_api_secret` and can be configured through the addon settings or the docker container create command.
| **Notification Settings**   | - **Critical Notification:** Generates an audible alert even when your device is in silent mode.<br/>- **Standard Notification:** Sends a traditional notification respecting your device's audio settings.<br/>- **None:** No notifications are sent in case of a failure.
| **Notification Service**  | The notification service of your choice for selecting a single device or a group of devices, instead of alerting all mobile devices registered in home assistant. The default is `notify.notify`, which notifies all devices.


## Credits

- **Greg Hesp ([@greghesp](https://github.com/greghesp))**: https://github.com/greghesp/ha-bambulab
- **Obico ([@TheSpaghettiDetective](https://github.com/TheSpaghettiDetective))**: https://github.com/TheSpaghettiDetective/obico-server
