ARG BUILD_FROM
FROM ${BUILD_FROM}

# paho-mqtt pinned to 1.x for the stable Client() API; icmplib for ICMP probing.
RUN pip install --no-cache-dir "paho-mqtt<2.0" "icmplib>=3.0"

COPY run.py /run.py

CMD ["python3", "/run.py"]
