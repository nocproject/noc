FROM alpine:3.22
COPY root/ /
RUN \
    apk add --no-cache openssh-server openssh-client \
    && /usr/bin/ssh-keygen -A \
    && adduser -S -h /home/test -s /bin/sh test \
    && (echo "test:pw1234567890" | /usr/sbin/chpasswd) \
    && chown -R test /home/test \
    && chmod 500 /home/test/.ssh \
    && chmod 400 /home/test/.ssh/*
CMD ["/usr/sbin/sshd", "-D", "-e", "-4"]