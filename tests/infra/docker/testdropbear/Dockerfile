FROM alpine:3.22
COPY root/ /
RUN \
    apk add --no-cache dropbear \
    && mkdir -p /etc/dropbear \
    && /usr/bin/dropbearkey -t rsa -f /etc/dropbear/dropbear_rsa_host_key -s 2048 \
    && /usr/bin/dropbearkey -t ecdsa -f /etc/dropbear/dropbear_ecdsa_host_key \
    && adduser -S -h /home/test -s /bin/sh test \
    && (echo "test:pw1234567890" | /usr/sbin/chpasswd) \
    && chown -R test /home/test \
    && chmod 500 /home/test/.ssh \
    && chmod 400 /home/test/.ssh/*
CMD ["/usr/sbin/dropbear", "-F", "-E"]
EXPOSE 22