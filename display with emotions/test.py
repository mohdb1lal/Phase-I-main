#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import spidev as SPI
sys.path.append("..")
from lib import LCD_2inch
from PIL import Image

# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 18
bus = 0
device = 0
logging.basicConfig(level=logging.DEBUG)

try:
    # Initialize the LCD display
    disp = LCD_2inch.LCD_2inch()
    disp.Init()
    disp.clear()
    disp.bl_DutyCycle(50)  # Set backlight brightness

    # Load the image
    image_path = '/home/prok/Downloads/project/Phase-I-main/Emo-main/Code/emotions/happy/frame24.png'  # Path to the image file
    image = Image.open(image_path)

    # Rotate the image if necessary (180 degrees)
    image = image.rotate(180)

    # Display the image on the LCD
    disp.ShowImage(image)
    logging.info("Image displayed successfully")

    # Keep the image displayed for 5 seconds
    time.sleep(5)

    # Clear the display and exit
    disp.module_exit()
    logging.info("Display cleared and exited")

except IOError as e:
    logging.info(f"IOError: {e}")
except KeyboardInterrupt:
    disp.module_exit()
    logging.info("Program interrupted and exited")
