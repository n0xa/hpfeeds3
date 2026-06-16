FROM alpine:3.22
LABEL version="2.2.5"
LABEL maintainer="n0xa"
# hadolint ignore=DL3018
RUN apk --no-cache add python3
RUN python3 -m venv /app

COPY requirements.txt /requirements.txt
RUN /app/bin/pip install -r requirements.txt

COPY setup.py /src/setup.py
COPY hpfeeds /src/hpfeeds
RUN /app/bin/pip install /src
RUN mkdir /app/var

RUN adduser -D -H -s /sbin/nologin -u 997 hpfeeds3 \
    && chown -R hpfeeds3:hpfeeds3 /app

USER hpfeeds3

WORKDIR /app/var
VOLUME /app/var

EXPOSE 10000/tcp

ENTRYPOINT ["/app/bin/hpfeeds-broker", "--bind=0.0.0.0:10000"]
