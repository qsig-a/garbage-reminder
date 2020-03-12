FROM python:3.7-slim-buster
RUN apt-get update && apt-get install -y
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
ARG DIR='/scripts'
ADD reminder.py $DIR/reminder.py
RUN pip install -r requirements.txt