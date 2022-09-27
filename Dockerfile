#Dockerfile, Image, Container
FROM python:3.9

ADD /DisplayDriver/ /DisplayDriver
ADD /AT-tracker /AT-tracker

RUN pip install Pillow spidev RPi.GPIO


CMD ["python", "/DisplayDriver/bus_timeV1.py"]