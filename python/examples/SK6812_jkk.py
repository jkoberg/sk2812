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
  
  def __init__(self, strip, count=LED_COUNT, fraction=0.01):
    self.strip = strip
    self.pixels = self.strip.getPixels()
    self.count = count
    self.batch = int(fraction * count)
    
  def step(self):
    for i in range(self.batch):
      self.pixels[random.randint(0,self.count-1)] = self.strobeColor


class Alternate:
  def __init__(self, strip, c=2, speed=1, color=Color(0,0,0,255)):
    self.pixels = strip.getPixels()
    self.count = strip.numPixels()
    self.color = color
    self.c = c
    self.speed = speed
    self.offset = 0

  def step(self, framecount):
    self.offset = (self.offset + self.speed) % self.count
    r = range(self.offset, self.offset + self.count, self.c)
    for i in r:
      self.pixels[i % self.count] = self.color


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

class BackgroundIO:
  def __init__(self, strip, fps=60):
    self.count = strip.numPixels()
    self.leds = strip.getPixels()
    self.strip = strip
    self.data = [
      [Color(0,0,0,0)] * self.count,
      [Color(0,0,0,0)] * self.count
      ]
    self.inq = Queue.Queue()
    self.outq = Queue.Queue()
    self.currentIdx = 0
    self.thread = threading.Thread(target = self.inner)
    self.thread.setDaemon(True)
    self.statsthread = threading.Thread(target = self.stats)
    self.statsthread.setDaemon(True)
    self.statsthread.start()
    self.t = None
    self.frametime = 1.0/fps
    self.framecount = 0
    self.cutlosses = self.frametime * -2
    self.currentIdx = 0
  def __getitem__(self, pos):
    return self.data[self.currentIdx][pos]
  def __setitem__(self, pos, value):
    self.data[self.currentIdx][pos] = value
  def getPixels(self):
    return self
  def numPixels(self):
    return self.count
  def show(self):
    lastidx = self.inq.get()
    #self.outq.put(self.inq.get())
    self.currentIdx = (self.currentIdx + 1) % 2
    self.outq.put(self.currentIdx)
    #print("show getting from inq")
    #print("show got from inq")
  def stats(self):
    t = time.time()
    frames = self.framecount
    while True:
      time.sleep(10)
      told = t
      t = time.time()
      framesold = frames
      frames = self.framecount
      fps = (frames - framesold) / (t - told)
      print("%0.3f fps"%(fps,))
  def inner(self):
    while True:
      #print("inner getting from outq")
      nextidx = self.outq.get()
      #print("innger got from outq: %s"%(nextidx,))
      if nextidx == "quit":
        self.inq.put(None)
        break
      if nextidx is None:
        continue
      self.leds[:] = self.data[nextidx]
      self.inq.put(nextidx)
      self.strip.show()
      time.sleep(0.002)
      self.framecount = self.framecount + 1
      if self.t is None:
        self.t = time.time() + self.frametime
      else:
        self.t = self.t + self.frametime
      dwell = self.t - time.time()
      if dwell <= self.cutlosses:
        self.t = None
      else:
        time.sleep(max(0.0, dwell))
  def startBackgroundThread(self):
    #print("init putting to outq")
    self.inq.put(0)
    self.inq.put(1)
    self.thread.start()
  def stopBackgroundThread(self):
    #print("stopBackgroundThread called")
    try:
      self.outq.put("quit")
      self.outq.put("quit")
    except Queue.Empty:
      pass

def fromHSV(h,s,v):
  r,g,b = colorsys.hsv_to_rgb(h,s,v)
  return Color(int(r*255), int(g*255), int(b*255))
    
# Main program logic follows:
if __name__ == '__main__':
  strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
  pixels = strip.getPixels()
  strip.begin()
  b = BackgroundIO(strip, fps=75)
  allBlack = [Color(0,0,0,0)] * strip.numPixels()
  print ('Press Ctrl-C to quit.')
  try:
    cw =  FastColorWheel(b, speed=1, reps=1, hsvv=0.7)
    bb =  Bars(b, speed=-0.5, widthfrac=0.3, reps=5)
    bb2 = Bars(b, speed=-0.6, reps=28, widthfrac=0.0, widthabs=3)

    a = Alternate(b, 4)
    aa = Alternate(b, 5, -1, fromHSV(0.6,1,1))

    hbb1 = Bars(b, speed=-.01, reps=int(strip.numPixels()/4.), widthfrac=0.0, widthabs=1, color=fromHSV(0.3,1.0,1.0))
    hbb2 = Bars(b, speed=.02, reps=int(strip.numPixels()/3.), widthfrac=0.0, widthabs=1, color=fromHSV(0.6,1.0,1.0))
    
    wb =  Bars(b, speed=2.1, reps=7, offset=13, widthfrac=0.0, widthabs=2, color=Color(0,0,0,255))
    wb2 = Bars(b, speed=-1.1, reps=5, offset=13, widthfrac=0.0, widthabs=10, color=Color(64,64,255,255))
    sp =  Spectac(b, fraction=1/20.)
    pol = Police(b)
    b.startBackgroundThread()
    while True:
      tfake = b.framecount * b.frametime
      tcycle = tfake % 20.0
      if(False and 0.0 <= tcycle < 5.0):
        pol.step(tfake)
      elif(True or 5.0 <= tcycle < 10.0):  
        #b[:] = allBlack
        #a.step(b.framecount)
        #aa.step(b.framecount)
        cw.step()
        #hbb1.step()
        #hbb2.step()
        #bb.step()
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
      b.show()
  except KeyboardInterrupt:
    print("exiting")
    b.stopBackgroundThread()
    time.sleep(0.25)
    strip.getPixels()[:] = [Color(0,0,0,0)] * strip.numPixels()
    strip.show()
    print("exited")
