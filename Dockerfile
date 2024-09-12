# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 8080

COPY . .

CMD ["gunicorn", "--workers", "4", "--worker-class", "gthread", "--threads", "2", "--timeout", "180", "-b", ":8080", "app:app"]
