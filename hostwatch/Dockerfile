# Home Assistant runs this container's CMD directly (init: false in config.yaml),
# so a plain Python base is enough — and unlike the bare HA base image it ships
# pip. python:3.12-alpine is a multi-arch manifest, so this builds on amd64 and
# aarch64 without a build.yaml / BUILD_FROM indirection.
FROM python:3.12-alpine

RUN pip install --no-cache-dir "paho-mqtt<2.0" "icmplib>=3.0"

COPY run.py /run.py

CMD ["python3", "/run.py"]
