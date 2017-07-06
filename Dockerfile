FROM python:3

RUN pip install watchdog docker-py jinja2

ADD watch.py ./watch.py