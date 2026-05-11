#!/bin/sh
apk add --no-cache wireguard-tools py3-requests py3-pyroute2
wg genkey | tee /app/privatekey | wg pubkey > /app/publickey
echo "WireGuard keys generated."
iperf3 -s -D
exec tail -f /dev/null
