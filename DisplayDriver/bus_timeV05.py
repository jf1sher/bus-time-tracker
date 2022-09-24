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

logging.basicConfig(level=logging.DEBUG)

next_update = 30
epd = epd1in54b_V2.EPD()
logging.info("init and Clear")
epd.init()
epd.Clear()
time.sleep(1)

font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

blackimage = Image.new('1', (epd.width, epd.height), 255)
redimage = Image.new('1', (epd.width, epd.height), 255)


try:
    while next_update >= 0:
        blackimage = Image.new('1', (epd.width, epd.height), 255)
        redimage = Image.new('1', (epd.width, epd.height), 255)
        # Drawing on the image
        logging.info("1.Drawing on the image...")
        
        drawblack = ImageDraw.Draw(blackimage)
        drawred = ImageDraw.Draw(redimage)

        drawblack.rectangle((0, 10, 200, 34), fill = 255)
        drawblack.text((8, 10), 'rainbow frends on roblox', font = font18, fill = 0)
      #  drawblack.text((8, 30), 'Route: 923', font = font18, fill = 0)
       # drawblack.text((8, 50), 'Stop:2332', font = font18, fill = 0)
        #drawblack.text((8, 100), 'Next Bus:', font = font18, fill = 0)
        #drawblack.text((8, 120), 'Leave at 12:30pm', font = font18, fill = 0)
        #drawblack.text((8, 160), 'Next Update in ' + str(next_update) + 's', font = font18, fill = 0)
        time.sleep(5)
        next_update -= 5

        blackimage = blackimage.transpose(Image.ROTATE_90) 
        redimage = redimage.transpose(Image.ROTATE_90)
        
        epd.display(epd.getbuffer(blackimage),epd.getbuffer(redimage))
    
    #logging.info("Goto Sleep...")
    #epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd1in54b_V2.epdconfig.module_exit()
    exit()

