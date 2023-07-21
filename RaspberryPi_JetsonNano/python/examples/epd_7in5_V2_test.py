#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys, argparse
import os
import requests
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2
import time
import requests
from PIL import Image,ImageDraw,ImageFont
import datetime
import traceback

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--force", action='store_true')
args = arg_parser.parse_args()

# Twilio
from twilio.rest import Client
account_sid = "ACxxx"
auth_token = "yyy"
client = Client(account_sid, auth_token)

# logging.basicConfig(level=logging.DEBUG)

def main():
    # # Get an MMS message
    # image_url = get_mms_url()
    # image = get_image(image_url)
    # if not image:
    #     return

    # Get an Inspirobot image
    image_url = get_inspirobot_url()
    image = get_image(image_url)
    if not image:
        return

    # Display the image
    display_image(image)
    return

def get_inspirobot_url():
    contents = requests.get("https://inspirobot.me/api?generate=true")
    print(contents.text)
    return contents.text

def get_mms_url():
    logging.info("epd - Checking for new image")
    messages = client.messages.list(
        to='+13125008555',
        limit=20
    )

    # Get the most recent 
    try:
        f = open("/home/alex/recent.txt", "r")
        recent_sid = f.read()
    except FileNotFoundError:
        recent_sid = ""
        

    for message in messages:
        if (message.num_media != "1"):
            continue
        if (message.sid == recent_sid and not args.force):
            logging.info("epd - Already showing")
            return
        for media in message.media.list():
            # Grab the first image
            media_url = 'https://api.twilio.com' + media.uri[:-5] # strip off the '.json'
            
            # Mark the most recent image
            f = open("recent.txt", "w")
            f.write(message.sid)
            f.close()
            # return the image url
            return media_url

def get_image(url):
    logging.info("epd - Pulling image with url " + url)
    # Load the image
    img = Image.open(requests.get(url, stream = True).raw)
    # Resize
    width, height = img.size
    source_ratio = width / height
    
    # contain
    desired_x = min(800, int(480 * source_ratio))
    desired_y = min(int(800 / source_ratio), 480)

    # # cover
    # desired_x = max(800, int(480 * source_ratio))
    # desired_y = max(int(800 / source_ratio), 480)

    img = img.resize((desired_x, desired_y), Image.ANTIALIAS)

    # Crop
    width, height = img.size
    crop_x = int((width - 800) / 2)
    crop_y = int((height - 480) / 2)
    area = (crop_x, crop_y, width - crop_x, height - crop_y)
    img = img.crop(area)
    
    # Make sure it's 800x480
    img = img.resize((800, 480), Image.ANTIALIAS)

    return img

def display_image(bitImage):
    logging.info("epd - Displaying image")
    try:
        epd = epd7in5_V2.EPD()

        epd.init()
        # epd.Clear()
        
        epd.display(epd.getbuffer(bitImage))
        # time.sleep(2)

        epd.sleep()
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in5_V2.epdconfig.module_exit()
        exit()

def run_display():
    try:
        logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()

        logging.info("init and Clear")
        epd.init()
        epd.Clear()

        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

        # Drawing on the Horizontal image
        logging.info("1.Drawing on the Horizontal image...")
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        draw.text((10, 0), 'hello world', font = font24, fill = 0)
        draw.text((10, 20), '7.5inch e-Paper', font = font24, fill = 0)
        draw.text((150, 0), u'微雪电子', font = font24, fill = 0)
        draw.line((20, 50, 70, 100), fill = 0)
        draw.line((70, 50, 20, 100), fill = 0)
        draw.rectangle((20, 50, 70, 100), outline = 0)
        draw.line((165, 50, 165, 100), fill = 0)
        draw.line((140, 75, 190, 75), fill = 0)
        draw.arc((140, 50, 190, 100), 0, 360, fill = 0)
        draw.rectangle((80, 50, 130, 100), fill = 0)
        draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
        epd.display(epd.getbuffer(Himage))
        time.sleep(2)

        # Drawing on the Vertical image
        logging.info("2.Drawing on the Vertical image...")
        Limage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Limage)
        draw.text((2, 0), 'hello world', font = font18, fill = 0)
        draw.text((2, 20), '7.5inch epd', font = font18, fill = 0)
        draw.text((20, 50), u'微雪电子', font = font18, fill = 0)
        draw.line((10, 90, 60, 140), fill = 0)
        draw.line((60, 90, 10, 140), fill = 0)
        draw.rectangle((10, 90, 60, 140), outline = 0)
        draw.line((95, 90, 95, 140), fill = 0)
        draw.line((70, 115, 120, 115), fill = 0)
        draw.arc((70, 90, 120, 140), 0, 360, fill = 0)
        draw.rectangle((10, 150, 60, 200), fill = 0)
        draw.chord((70, 150, 120, 200), 0, 360, fill = 0)
        epd.display(epd.getbuffer(Limage))
        time.sleep(2)

        logging.info("3.read bmp file")
        Himage = Image.open(os.path.join(picdir, '7in5_V2.bmp'))
        epd.display(epd.getbuffer(Himage))
        time.sleep(2)

        logging.info("4.read bmp file on window")
        Himage2 = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
        Himage2.paste(bmp, (50,10))
        epd.display(epd.getbuffer(Himage2))
        time.sleep(2)

        logging.info("Clear...")
        epd.init()
        epd.Clear()

        logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in5_V2.epdconfig.module_exit()
        exit()

def full_reset():
    logging.info("epd - Doing a full reset")
    try:
        epd = epd7in5_V2.EPD()

        epd.init()
        epd.Clear()
        epd.sleep()
    
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in5_V2.epdconfig.module_exit()
        exit()
    return

if __name__ == "__main__":
    if (args.force):
        full_reset()
    main()