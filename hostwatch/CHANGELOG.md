# Changelog

## 0.1.1

- Build from `python:3.12-alpine` directly instead of via `BUILD_FROM`/`build.yaml`;
  the Supervisor was injecting the pip-less HA base image, breaking the build.

## 0.1.0

- Initial release.
- Monitor hosts over ICMP or TCP with per-host intervals and timeouts.
- Publish one `binary_sensor` (device class `connectivity`) per host via MQTT
  discovery, with an availability topic.
- Broker auto-discovered from the Supervisor MQTT service.
