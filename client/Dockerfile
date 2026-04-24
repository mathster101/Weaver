FROM alpine:3.19

RUN apk add --no-cache python3 py3-pip wireguard-tools iperf3 vim neofetch traceroute

WORKDIR /app
COPY app/ .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
