FROM ftvsubtil/alpine-ffmpeg:release-1.0.0

WORKDIR /app
ADD . .

RUN apk update && \
    apk add python3 && \
    pip3 install -r requirements.txt

CMD python3 src/worker.py
