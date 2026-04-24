#!/bin/sh
apk add --no-cache wireguard-tools
wg genkey | tee /app/privatekey | wg pubkey > /app/publickey
echo "WireGuard keys generated."
iperf3 -s -D
exec tail -f /dev/null
