#!/bin/sh
apk add --no-cache wireguard-tools py3-requests py3-pyroute2
iperf3 -s -D
exec tail -f /dev/null
