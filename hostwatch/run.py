#!/usr/bin/env python3
"""Hostwatch: a fast host up/down monitor for Home Assistant.

Probes each configured host over ICMP or TCP on a short, per-host interval and
publishes a connectivity ``binary_sensor`` per host to Home Assistant via MQTT
discovery. A machine going to sleep, powering off, or coming back shows within
one interval, far faster than the built-in ping integration's fixed poll.

Runs as a Home Assistant add-on: options come from ``/data/options.json`` and
the MQTT broker is discovered from the Supervisor services API, so the user
never types broker credentials.
"""
import json
import os
import socket
import time
import urllib.request

import paho.mqtt.client as mqtt

try:
    from icmplib import ping as icmp_ping
    _HAVE_ICMP = True
except Exception:  # pragma: no cover - icmplib always vendored, but be safe
    _HAVE_ICMP = False

SUPERVISOR = "http://supervisor"
TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
DISCOVERY_PREFIX = "homeassistant"
BASE = "hostwatch"
AVAIL_TOPIC = f"{BASE}/status"


def log(*a):
    print("[hostwatch]", *a, flush=True)


def load_options():
    with open("/data/options.json") as f:
        return json.load(f)


def mqtt_config():
    """Broker connection details from the Supervisor MQTT service."""
    req = urllib.request.Request(
        f"{SUPERVISOR}/services/mqtt",
        headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.load(r)["data"]
    return {
        "host": data["host"],
        "port": int(data["port"]),
        "username": data.get("username") or None,
        "password": data.get("password") or None,
    }


def slugify(s):
    out = "".join(c.lower() if c.isalnum() else "_" for c in s)
    while "__" in out:
        out = out.replace("__", "_")
    return out.strip("_") or "host"


def probe_tcp(host, port, timeout):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def probe_icmp(host, timeout):
    if not _HAVE_ICMP:
        return False
    # Try unprivileged (SOCK_DGRAM) first; fall back to raw sockets, which need
    # the container's default CAP_NET_RAW.
    for privileged in (False, True):
        try:
            return icmp_ping(host, count=1, timeout=timeout,
                             privileged=privileged).is_alive
        except Exception:
            continue
    return False


def probe(h, default_timeout):
    timeout = int(h.get("timeout", default_timeout))
    if h.get("method", "icmp") == "tcp":
        return probe_tcp(h["host"], int(h.get("port", 22)), timeout)
    return probe_icmp(h["host"], timeout)


def build_entries(hosts, default_interval):
    entries = []
    seen = set()
    for h in hosts:
        sid = slugify(h.get("name") or h["host"])
        base_sid, n = sid, 2
        while sid in seen:  # keep unique_ids distinct on duplicate names
            sid = f"{base_sid}_{n}"
            n += 1
        seen.add(sid)
        entries.append({
            "cfg": h,
            "sid": sid,
            "label": h.get("name") or h["host"],
            "state_topic": f"{BASE}/{sid}/state",
            "disc_topic": f"{DISCOVERY_PREFIX}/binary_sensor/{BASE}_{sid}/config",
            "interval": int(h.get("interval", default_interval)),
        })
    return entries


def publish_discovery(client, e):
    payload = {
        "name": e["label"],
        "unique_id": f"{BASE}_{e['sid']}",
        "object_id": f"{BASE}_{e['sid']}",
        "device_class": "connectivity",
        "state_topic": e["state_topic"],
        "payload_on": "ON",
        "payload_off": "OFF",
        "availability_topic": AVAIL_TOPIC,
        "device": {
            "identifiers": [BASE],
            "name": "Hostwatch",
            "manufacturer": "Hostwatch",
            "model": "Host monitor",
        },
    }
    client.publish(e["disc_topic"], json.dumps(payload), retain=True)


def main():
    o = load_options()
    default_interval = int(o.get("interval", 5))
    default_timeout = int(o.get("timeout", 2))
    hosts = o.get("hosts") or []
    if not hosts:
        log("no hosts configured; nothing to do")
        return

    mc = mqtt_config()
    client = mqtt.Client(client_id="hostwatch")
    if mc["username"]:
        client.username_pw_set(mc["username"], mc["password"])
    client.will_set(AVAIL_TOPIC, "offline", retain=True)
    log(f"connecting to MQTT {mc['host']}:{mc['port']}")
    client.connect(mc["host"], mc["port"], keepalive=60)
    client.loop_start()
    client.publish(AVAIL_TOPIC, "online", retain=True)

    entries = build_entries(hosts, default_interval)
    for e in entries:
        publish_discovery(client, e)
        log(f"monitoring {e['label']} "
            f"({e['cfg'].get('method', 'icmp')}, every {e['interval']}s)")

    last = {}
    nextdue = {e["sid"]: 0.0 for e in entries}
    while True:
        now = time.time()
        for e in entries:
            if now < nextdue[e["sid"]]:
                continue
            state = "ON" if probe(e["cfg"], default_timeout) else "OFF"
            if last.get(e["sid"]) != state:
                client.publish(e["state_topic"], state, retain=True)
                last[e["sid"]] = state
                log(f"{e['label']}: {state}")
            nextdue[e["sid"]] = now + e["interval"]
        time.sleep(0.5)


if __name__ == "__main__":
    main()
