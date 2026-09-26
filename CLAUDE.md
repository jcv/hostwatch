# CLAUDE.md

Guidance for Claude Code in this repo. `README.md` is the user-facing description and install
guide; this file holds the build context that used to sit in the `~/Projects` index row.

## Context

Moved from the Projects index 2026-09-26.

- **Why it exists:** built 2026-09-21 to drive the Home Assistant "AI" dashboard machine power
  buttons (wake/sleep Wraith, wake/shutdown Banshee), which need host state within seconds.
- **Stack:** Python (`paho-mqtt` + `icmplib`) on `FROM python:3.12-alpine`, because the HA base
  image lacks pip; `init: false` in `hostwatch/config.yaml`. Requires an MQTT broker.
- **Distribution:** custom-repo URL only (`https://github.com/jcv/hostwatch`), since HA has no add-on
  submission or review process. The README's My Home Assistant "add repository" button is the
  install path.
- **Future reuse:** a self-hosted phone-to-terminal share relay would reuse this add-on's packaging
  pattern; see `~/Projects/shortcuts/self-hosted-phone-share-pipeline.md`.
