
module leds;

import std.stdio;
import std.stdint;
import std.datetime;
import core.stdc.stdlib;
import core.thread;
import core.sys.posix.signal;
import std.math;

import colorspace_float;
import ws2811;


enum int count = 288;
enum float fps = 75.0;
enum cwspeed = (360/fps);
enum float reps = 1.0;
enum num cwsat = 1.0;
enum num cwvalue = 1.0;


ws2811_led_t  rgb (uint8_t r, uint8_t g, uint8_t b, uint8_t w=0) {
	return (w << 24) + (r << 16) + (g << 8) + b;
}

ws2811_led_t  hsv (num h=1.0, num s=1.0, num v=1.0, num gamma=2.4) {
	num r,g,b;
	uint8_t ri, gi, bi;
	Hsv2Rgb(&r, &g, &b, h, s, v);
	ri = cast(uint8_t)(pow(r, gamma) *255);
	gi = cast(uint8_t)(pow(g, gamma) *255);
	bi = cast(uint8_t)(pow(b, gamma) *255);
	return rgb(ri, gi, bi);
}

void  check (ws2811_return_t ret) {
	if(ret != ws2811_return_t.WS2811_SUCCESS) {
		printf("ws2811 error: %d\n", ret);
	}
}


extern(C) ws2811_t  strip = {
		freq: 1000000,
		dmanum: 5,
		channel: [{
			gpionum: 18,
			count: count,
			invert: 0,
			brightness: 255,
			strip_type: SK6812_STRIP_GRBW,
		}, {
			gpionum:0,
			count:0,
			brightness:0
		}]
	};



int keepRunning = 1;

extern (C) void exit(int s) {
	keepRunning = 0;
}

void onexit() {
	printf("Exiting.\n");
	ws2811_wait(&strip);
	strip.channel[0].leds[0..count] = rgb(0,0,0);
	ws2811_render(&strip);
	ws2811_fini(&strip);
}



void main() {
	sigset(SIGINT, &exit);

	check( ws2811_init(&strip) );
	auto leds = strip.channel[0].leds;

	StopWatch sw;
	sw.start();
	auto frametime = cast(int)(1000000000 / fps);
	auto tnext = sw.peek().nsecs + frametime;
	num h = 0.0;
	int frames = 0;
	num pixelangle = 360.0/count;
	while(keepRunning) {
		h += cwspeed;
		if(h>=360.) 
			h -= 360.0;
		for(int j = 0; j < count; j++) {
			auto offset = j * pixelangle * reps;
			auto c = hsv(h + offset, cwsat, cwvalue);
			leds[j] = c;
		}
		ws2811_wait(&strip);
		ws2811_render(&strip);
		auto dwell = tnext - (sw.peek().nsecs);
		if(dwell > 0) { 
			Thread.sleep( dwell.nsecs );
		}
		tnext = tnext + frametime;
		frames += 1;
	}
	sw.stop();
	auto msecs = sw.peek().msecs;
	auto observedfps = frames / (msecs/1000.0);
	printf("Got %0.2f fps\n", observedfps);
	onexit();
}
