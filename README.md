
# Bouygues Bbox Router

This a *custom component* for [Home Assistant](https://www.home-assistant.io/).
The `bbox2` integration allows you to observe and control [Bbox router](http://www.bouygues.fr/).

There is currently support for the following device types within Home Assistant:

* Sensor with traffic metrics
* Binary Sensor with wan status , public ip , private ip
* Device tracker for connected devices (via option add wired devices)
* Switch for enable/disable Wireless and Guest Wifi
* Press button to restart box
* Press button to ring phone

![GitHub release](https://img.shields.io/github/release/Cyr-ius/hass-bbox2)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-bouygues.svg)](https://github.com/hacs/integration)

## Configuration

The preferred way to setup the Bouygues Bbox platform is by enabling the discovery component.

Add Bouygues Bbox module via HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=cyr-ius&repository=hass-bbox2&category=integration)

Add your device via the Integration menu

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=bbox2)

### Initial setup

You must have set a password for your Bbox router web administration page. 

The first time Home Assistant will connect to your Bbox, you will need to specify the password of bbox.

### Supported routers

Only the routers with Bbox OS are supported:

* Bbox (all versions)

## Presence Detection

This platform offers presence detection by keeping track of the
devices connected to a [Bbox](http://www.bouygues.fr/) router.

Ability to disable this option by integration options

### Notes

Note that the Bbox waits for some time before marking a device as inactive, meaning that there will be a small delay (1 or 2 minutes) between the time you disconnect a device and the time it will appear as "away" in Home Assistant.

You should take this into account when specifying the `consider_home` parameter.
On the contrary, the Bbox immediately reports devices newly connected, so they should appear as "home" almost instantly, as soon as Home Assistant refreshes the devices states.

## Sensor

This platform offers you sensors to monitor a Bbox router. The monitored conditions are instant upload and download rates in Mb/s.
