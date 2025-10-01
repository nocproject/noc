FROM alpine:3.22
RUN \
    apk add --no-cache net-snmp
COPY root/ /
CMD ["/usr/sbin/snmpd", "-f", "-Lo:", "-d", "-a", "udp:161"]
EXPOSE 161/udp