FROM python:3.9-alpine

RUN addgroup -S rysolv_monitor && adduser -S rysolv_monitor -G rysolv_monitor

RUN apk add --update --virtual builddeps gcc musl-dev libffi-dev openssl-dev

WORKDIR /usr/src/app

COPY ./requirements.txt ./requirements.txt

RUN pip install -rrequirements.txt

COPY . .

RUN python setup.py install

RUN rm -r ./* && apk del builddeps

#COPY ./config.yaml .

USER rysolv_monitor

ENTRYPOINT ["python"]

CMD ["-m", "rysolv_monitor"]
