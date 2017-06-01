# NeoPixel library strandtest examplE
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.


import time, random, colorsys, collections, sys, threading, Queue, os, traceback

from neopixel import *

# LED strip configuration:
LED_COUNT      = 288      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 1000000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0
#LED_STRIP      = ws.SK6812_STRIP_RGBW  
LED_STRIP      = ws.SK6812W_STRIP


class Spectac:
  strobeColor = Color(255,255,255,255)
  offColor = Color(0,0,0,0)
  def __init__(self, strip, count=LED_COUNT, fraction=0.01):
    self.strip = strip
    self.pixels = self.strip.getPixels()
    self.count = count
    self.batch = int(fraction * count)
    self.indexes = range(count)
    self.half = int(self.count * 0.5) + self.batch
    random.shuffle(self.indexes)
  def step(self):
    lastround = self.indexes[:self.batch]
    thisround = self.indexes[self.batch:self.half]
    rest = self.indexes[self.half:]
    for i in lastround:
      self.pixels[i] = self.offColor
    random.shuffle(thisround)
    self.indexes = thisround + rest + lastround
    for i in self.indexes[:self.batch]:
      self.pixels[i] = self.strobeColor


class ColorWheel:
  def __init__(self, strip, speed=1.0, offset=0.0, reps=0.25, hsvv=0.03, hstart=0.0, hend=1.0, count=LED_COUNT):
    self.speedDivided = float(speed)/count # units of pixels per iteration
    self.offset = offset # units of strips
    self.strip = strip
    self.pixels = strip.getPixels()
    self.perPixel = float(reps) / count
    self.count = count
    self.reps = reps # units of reps per LED_COUNT
    self.hsvv=hsvv  
    self.hstart = hstart
    self.hend = hend
  def step(self):
    self.offset = (self.offset + self.speedDivided) % 1.0
    for i in range(self.count):
      h = ( (i * self.perPixel) + self.offset) % 1.0
      self.pixels[i] = Color(*(int(c*255) for c in colorsys.hsv_to_rgb(h, 1.0, self.hsvv)))

class FastColorWheel:
  def mincolor(self, r,g,b):
    m = min(r,g,b)
    return Color(r-m, g-m, b-m, m)
  def __init__(self, strip, speed=1, reps=1, hsvv=0.03, count=LED_COUNT):
    self.strip = strip
    self.speed = speed
    self.reps = reps
    self.hsvv = hsvv 
    self.count = count
    self.pixels = self.strip.getPixels()
    huefuzz = random.random()
    self.pixelvalues = collections.deque([
      self.mincolor(*(int((i**2.2)*255) for i in colorsys.hsv_to_rgb(
        (huefuzz + ( (float(n)/self.count) * self.reps)) % 1.0,
        1.0,
        self.hsvv
        ))) 
      for n in range(count)
          ])
  def step(self):
    self.pixelvalues.rotate(self.speed)
    self.pixels[:] = self.pixelvalues
    

class Bars:
  def __init__(self, strip, speed=-0.1, reps=5, offset=0.0, widthfrac=0.5, widthabs=0, color=Color(0,0,0,0)):
    self.strip = strip
    self.leds = strip.getPixels()
    self.color = color
    self.widthfrac = widthfrac
    self.widthabs = widthabs
    self.speed = speed
    self.count = strip.numPixels()
    self.reps = reps
    self.sectorwidth = float(self.count) / self.reps # pixels
    self.lightedwidth = self.sectorwidth * self.widthfrac # pixels
    self.sectorstarts = [(n * self.sectorwidth) for n in range(self.reps)]
    self.offset = offset 
  def modrange(self, start, end, modulus):
    s,e = (start % modulus, end % modulus)
    if s <= e:
      return range(s, e)
    return (range(s, modulus) + range(0, e))
  def step(self):
    self.offset = (self.offset + self.speed) % self.count # pixels
    starts = [self.offset + s for s in self.sectorstarts]
    for start in starts:
      end = start + self.lightedwidth + self.widthabs
      for i in self.modrange(int(start), int(end), self.count):
        self.leds[i] = self.color

class Police:
  off = Color(0,0,0,0)
  strobeBlue = Color(0,0,255,64)
  strobeWhite = Color(255,0,0,64)
  def __init__(self, strip):
    self.strip = strip
    self.count = strip.numPixels()
    self.leds = strip.getPixels()
    self.tstrobe = 0.0
    self.strobePhase = 0
  def step(self, abst):
    t = abst % 4.0
    if 0.0 <= t < 1:
      rt = t
      color = [30,0,0]
    elif 1 <= t < 2:
      rt = 1-(t-1)
      color = [30,0,0]
    elif 2 <= t < 3:
      rt = t-2
      color = [0,0,20]
    elif 3 <= t < 4:
      rt = 1-(t-3)
      color = [0,0,20]
    else:
      color = [0,0,0]
    final = Color(*(int(rt * component) for component in color))
    self.leds[:] = [final] * self.count
    if(abst >= self.tstrobe):
      if(self.strobePhase == 0):
        self.leds[:] = [self.strobeWhite] * self.count
        self.strobePhase = 1
      elif(self.strobePhase == 1):
        self.leds[:] = [self.off] * self.count
        self.tstrobe = abst + 0.1  
        self.strobePhase = 2
      elif(self.strobePhase == 2):
        self.leds[:] = [self.strobeBlue] * self.count
        self.strobePhase = 3
      elif(self.strobePhase == 3):
        self.leds[:] = [self.off] * self.count
        self.tstrobe = abst + 0.9
        self.strobePhase = 0


class Buffer:
  def __init__(self, strip):
    self.strip = strip
    self._pixels = strip.getPixels()
    self.data = [Color(0,0,0,0)] * strip.numPixels()

  def getPixels(self):
    return self.data

  def numPixels(self):
    return len(self.data)

  def __getitem__(self, pos):
    return self.data[pos]

  def __setitem__(self, pos, value):
    self.data[pos] = value

  def show(self):
    self._pixels[:] = self.data
    self.strip.show()


# Main program logic follows:
if __name__ == '__main__':
  rawstrip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
  rawstrip.begin()
  strip = Buffer(rawstrip)
  framecount = 0
  frametime = 1/75.0
  print ('Press Ctrl-C to quit.')
  try:
    cw =  FastColorWheel(strip, speed=1, reps=1, hsvv=0.9)
    bb =  Bars(strip, speed=-0.5, widthfrac=0.3, reps=5)
    bb2 = Bars(strip, speed=-0.6, reps=28, widthfrac=0.0, widthabs=3)
    wb =  Bars(strip, speed=2.1, reps=7, offset=13, widthfrac=0.0, widthabs=2, color=Color(0,0,0,255))
    wb2 = Bars(strip, speed=-1.1, reps=5, offset=13, widthfrac=0.0, widthabs=10, color=Color(64,64,255,255))
    sp =  Spectac(strip, fraction=1/50.)
    pol = Police(strip)
    tnext = time.time()
    while True:
      time.sleep(max(0, time.time() - tnext))
      tfake = framecount * frametime
      tcycle = tfake % 20.0
      if(False and 0.0 <= tcycle < 5.0):
        pol.step(tfake)
      elif(True or 5.0 <= tcycle < 10.0):  
        cw.step()
        bb.step()
        #bb2.step()
        #sp.step()
        #wb.step()
        #wb2.step()
      elif(10.0 <= tcycle < 15.0):
        #cw.step()
        #bb.step()
        #bb2.step()
        sp.step()
        #wb.step()
        #wb2.step()
      elif(15.0 <= tcycle < 20.0):
        #cw.step()
        bb.step()
        bb2.step()
        #sp.step()
        wb.step()
        wb2.step()
      strip.show()
      framecount = framecount + 1
      tnext = tnext + frametime
  except KeyboardInterrupt:
    print("exiting")
    time.sleep(0.1)
    strip.getPixels()[:] = [Color(0,0,0,0)] * strip.numPixels()
    strip.show()
    print("exited")
