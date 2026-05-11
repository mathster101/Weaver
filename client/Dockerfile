FROM alpine:3.19

RUN apk add --no-cache python3 py3-pip wireguard-tools iperf3 vim neofetch traceroute

WORKDIR /app
COPY app/ .
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
