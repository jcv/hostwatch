# Hostwatch

Fast host up/down monitoring for Home Assistant. Hostwatch probes each host you
list over **ICMP** (ping) or **TCP** (connect to a port) on a short, per-host
interval and publishes a `binary_sensor` (device class `connectivity`) per host
via **MQTT discovery**. A host sleeping, powering off, or coming back shows in
Home Assistant within one interval — seconds, not the minutes the built-in ping
integration takes.

## Requirements

- An **MQTT broker** (e.g. the Mosquitto broker add-on) and the Home Assistant
  **MQTT integration** configured. Hostwatch discovers the broker automatically
  from the Supervisor — you do not enter credentials.

## Configuration

```yaml
interval: 5        # default seconds between probes (per host can override)
timeout: 2         # default seconds to wait for a probe to answer
hosts:
  - name: NAS            # ICMP ping (default)
    host: 192.168.1.20
  - name: Desktop        # TCP probe — use for hosts that block ICMP
    host: 192.168.1.30
    method: tcp
    port: 3389
    interval: 3          # this host checked every 3s
```

| Option | Description |
| ------ | ----------- |
| `interval` | Default seconds between probes. Override per host. |
| `timeout` | Default seconds to wait before marking a host down. Override per host. |
| `hosts[].name` | Friendly name; also drives the entity id (`binary_sensor.hostwatch_<name>`). |
| `hosts[].host` | IP address or hostname. |
| `hosts[].method` | `icmp` (default) or `tcp`. |
| `hosts[].port` | TCP port to connect to when `method: tcp`. |
| `hosts[].interval` / `hosts[].timeout` | Optional per-host overrides. |

### ICMP vs TCP

- **ICMP** is the classic ping — universal, but a host that blocks ICMP (many
  Windows machines by default) reads as *down* even when it is up.
- **TCP** connects to a port you know is open when the host is up (e.g. `22`
  for SSH, `3389` for RDP). Use it for machines that block ICMP, and it is a
  reliable "is it usable right now" signal since a sleeping/off host refuses it.

## Entities

One `binary_sensor` per host, device class `connectivity` (**Connected** /
**Disconnected**), grouped under a single *Hostwatch* device. Entity ids are
`binary_sensor.hostwatch_<slug-of-name>`. If the add-on stops, its sensors go
`unavailable` (via the MQTT availability topic).

## Notes

- ICMP uses raw/datagram sockets; it works with the container's default
  capabilities. If ICMP does not work in your environment, use `method: tcp`.
- Prior art: [ping2mqtt](https://github.com/skullydazed/ping2mqtt) does ICMP →
  MQTT. Hostwatch adds a TCP probe, per-host sub-interval timing, and add-on
  packaging.
