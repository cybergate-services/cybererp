FROM alpine:3.8 as dev

RUN mkdir /services && mkdir /var/log/supervisor

RUN apk --no-cache add libxml2-dev libxslt-dev python3-dev build-base

RUN CFLAGS=-I/usr/include/libxml2/ LDFLAGS=-L/usr/lib pip3 install aiohttp-xmlrpc

COPY ./asterisk/services/requirements.txt /services/requirements.txt
RUN pip3 install -r /services/requirements.txt

FROM alpine:3.8

RUN mkdir /var/log/supervisor && apk --no-cache add python3 git sudo supervisor \
    libxml2 libxslt iptables ipset \
    asterisk asterisk-sample-config asterisk-sounds-en asterisk-sounds-moh asterisk-srtp \
    tcpdump ethtool vlan iftop ngrep bash vim screen tmux curl putty

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

COPY --from=dev /usr/lib/python3.6/site-packages/ /usr/lib/python3.6/site-packages/
COPY --from=dev /usr/lib/libc.so /usr/lib/libc.so

COPY ./asterisk/etc/ /etc/

COPY ./asterisk/services/ /services/

COPY ./asterisk/docker-entrypoint.sh /

EXPOSE 5060/udp 5038 8010

WORKDIR /services

ENTRYPOINT ["/docker-entrypoint.sh"]
