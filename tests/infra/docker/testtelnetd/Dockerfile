FROM alpine:3.22
COPY root/ /
RUN \
    apk add --no-cache busybox-extras \
    && adduser -S -h /home/test -s /bin/sh test \
    && (echo "test:pw1234567890" | /usr/sbin/chpasswd) 
CMD ["/usr/sbin/telnetd", "-F"]
EXPOSE 23