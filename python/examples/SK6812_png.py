#!/usr/bin/env python2

import time, random, colorsys, collections, sys, threading, Queue, os
from PIL import Image
from neopixel import *

# LED strip configuration:
LED_COUNT      = 288    # Number of LED pixels.
LED_PIN        = 18    # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 1000000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5     # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255   # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0
#LED_STRIP      = ws.SK6812_STRIP_RGBW  
LED_STRIP      = ws.SK6812W_STRIP


def all(strip, c=Color(0,0,0,0), show=True):
  strip.getPixels()[:] = [c]*strip.numPixels()


class ImageWipe:
  def __init__(self, count, leds, filename):
    self.count = count
    self.leds = leds
    self.i = Image.open(filename)
    w,self.h = self.i.size
    self.y = 0
    self.rows = [[]] * self.h
    
  def WGamColor(self, r,g,b):
    wmin = min(r,g,b)
    if r > 240 and g > 240 and b > 240:
      return Color(r,g,b, 255)
    return Color(r,g,b)

  def step(self):
    if self.rows[self.y] == []:
        self.rows[self.y] = [self.WGamColor(*self.i.getpixel((x,self.y))) for x in range(self.count)]
    self.leds[:] = self.rows[self.y]
    self.y = (self.y + 1) % self.h
    


# Main program logic follows:
if __name__ == '__main__':
  strip = Adafruit_NeoPixel(
      LED_COUNT,
      LED_PIN,
      LED_FREQ_HZ,
      LED_DMA,
      LED_INVERT,
      LED_BRIGHTNESS,
      LED_CHANNEL,
      LED_STRIP
      )
  strip.begin()

  print ('Press Ctrl-C to quit.')
  try:
    frametime = 1/60.
    im = ImageWipe(strip.numPixels(), strip.getPixels(), sys.argv[1])
    print("here we go")
    tnext = time.time()
    while True:
      im.step()
      strip.show()
      tnext = tnext + frametime
      dwell = tnext - time.time()
      if dwell < -frametime:
        tnext = time.time() + frametime
      time.sleep(max(0.0, dwell))
  finally:
    all(strip, Color(0,0,0,0))
    strip.show()



