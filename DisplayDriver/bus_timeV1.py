#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd1in54b_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback    

#Backend connection
sys.path.insert(0, '../AT-tracker')
import backend

route_name = "923"
stop_number = "3907"

def update_backend():
    next_bus_time, actual_bus_time = backend.get_next_bus(route_name, stop_number)
    bus_stop_name = backend.get_stop_word_name(stop_number)
    return next_bus_time, actual_bus_time,  bus_stop_name

logging.basicConfig(level=logging.DEBUG)

epd = epd1in54b_V2.EPD()
logging.info("init and Clear")
epd.init()
epd.Clear()
time.sleep(1)

try:
    font = ImageFont.truetype(os.path.join('Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join('Font.ttc'), 18)
except:
    logging.info("Font.ttc not found, using default font.")
    font = ImageFont.load_default()
    font18 = ImageFont.load_default()


blackimage = Image.new('1', (epd.width, epd.height), 255)
redimage = Image.new('1', (epd.width, epd.height), 255)


try:
    while True:
        next_bus_time, actual_bus_time, bus_stop_name = update_backend()
        if next_bus_time == "[]" or next_bus_time == "":
            next_bus_time = "No actives"
        if actual_bus_time == "no data" or actual_bus_time == "" or actual_bus_time == "[]":
            actual_bus_time = "No data"
        blackimage = Image.new('1', (epd.width, epd.height), 255)
        redimage = Image.new('1', (epd.width, epd.height), 255)
        # Drawing on the image
        logging.info("1.Drawing on the image...")
        
        drawblack = ImageDraw.Draw(blackimage)
        drawred = ImageDraw.Draw(redimage)

        drawblack.rectangle((0, 10, 200, 34), fill = 255)
        drawblack.text((8, 30), 'Route: ' + route_name, font = font18, fill = 0)
        drawblack.text((8, 50), 'Stop: ' + bus_stop_name, font = font18, fill = 0)
        drawblack.text((8, 100), 'Live arrival: ' + actual_bus_time, font = font18, fill = 0)
        drawblack.text((8, 120), 'Sch arrival: ' + next_bus_time, font = font18, fill = 0)
        drawblack.text((8, 160), 'Next Update in 60s', font = font18, fill = 0)
        

        blackimage = blackimage.transpose(Image.ROTATE_90) 
        redimage = redimage.transpose(Image.ROTATE_90)
        
        epd.display(epd.getbuffer(blackimage),epd.getbuffer(redimage))
        time.sleep(60)
        #epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd1in54b_V2.epdconfig.module_exit()
    exit()

