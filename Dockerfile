FROM alpine:3.7
RUN apk --no-cache add python3
RUN python3 -m venv /app

COPY requirements.txt /requirements.txt
RUN /app/bin/pip install -r requirements.txt

COPY setup.py /src/setup.py
COPY hpfeeds /src/hpfeeds
RUN /app/bin/pip install /src
RUN mkdir /app/var
WORKDIR /app/var
VOLUME /app/var

EXPOSE 10000/tcp

ENTRYPOINT ["/app/bin/hpfeeds-broker", "--bind=0.0.0.0:10000"]
