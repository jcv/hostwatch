# Hostwatch — Home Assistant add-on

[![Add repository to your Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fjcv%2Fhostwatch)

Fast host up/down monitoring for Home Assistant. Hostwatch probes your machines
over **ICMP or TCP** every few seconds and publishes a `binary_sensor` (device
class `connectivity`) per host via **MQTT discovery**, so a box sleeping,
powering off, or coming back shows in Home Assistant within seconds — not the
minutes the built-in ping integration takes.

## Why not just use…

- **Built-in Ping integration** — a slow, fixed poll, and `consider_home` holds
  a host "home" for minutes. Not tunable to seconds.
- **Uptime Kuma** — a great general uptime dashboard, but a **20s minimum**
  check interval, no native per-host HA entities (it integrates via
  webhooks/notifications), and it's a full Node + DB + web-UI app.
- **[ping2mqtt](https://github.com/skullydazed/ping2mqtt)** — the closest prior
  art (ICMP → MQTT discovery) and the inspiration here. Hostwatch adds a **TCP
  probe** so hosts that block ICMP (many Windows machines by default) still
  register, plus per-host sub-10s intervals and Home Assistant add-on packaging.

## Install

1. Click the button above, or in Home Assistant go to **Settings → Add-ons →
   Add-on Store → ⋮ → Repositories** and add
   `https://github.com/jcv/hostwatch`.
2. Install **Hostwatch** from the store, add your hosts in the Configuration
   tab, and start it.

Requires an **MQTT broker** (e.g. the Mosquitto broker add-on) with the MQTT
integration configured. Hostwatch discovers the broker automatically — no
credentials to enter.

## Configure

```yaml
interval: 5
timeout: 2
hosts:
  - name: NAS
    host: 192.168.1.20        # ICMP ping (default)
  - name: Desktop
    host: 192.168.1.30        # blocks ICMP → use TCP
    method: tcp
    port: 3389
    interval: 3
```

Each host becomes `binary_sensor.hostwatch_<name>` (device class connectivity),
grouped under one *Hostwatch* device. Full reference: [hostwatch/DOCS.md](hostwatch/DOCS.md).

## License

[MIT](LICENSE).
