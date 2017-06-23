
module leds;

import std.stdio;
import std.stdint;
import std.datetime;
import std.algorithm;
import core.stdc.stdlib;
import core.thread;
import core.sys.posix.signal;
import std.math;

import colorspace_float;
import ws2811;


enum int count = 288;
enum int bandwidth = 1000000;
enum float reps = 1.0;
enum num cwsat = 1.0;
enum num cwvalue = 1.0;

enum int frameoverhead = cast(int) (bandwidth * 0.0019);
enum int pixoverhead = 0;
enum int pixbits = pixoverhead + 32;
enum int framebits = frameoverhead + (pixbits * count);
enum float fps = bandwidth / framebits; 
enum cwspeed = (360/fps)/10;
enum int round = fps > 200 ? 0 :  cast(int) max(1, fps / 48.0);

ws2811_led_t  rgb (uint8_t r, uint8_t g, uint8_t b, uint8_t w=0) {
	return (w << 24) + (r << 16) + (g << 8) + b;
}


ws2811_led_t hsv(num h=1.0, num s=1.0, num v=1.0, num gamma=2.8) {
	num r,g,b;
	uint8_t ri, gi, bi;
	Hsv2Rgb(&r, &g, &b, h, s, v);
	ri = cast(uint8_t)(pow(r, gamma) * 255);
	gi = cast(uint8_t)(pow(g, gamma) * 255);
	bi = cast(uint8_t)(pow(b, gamma) * 255);
	return rgb(ri, gi, bi);
}

enum uint chans = 4;

void  check (ws2811_return_t ret) {
	if(ret != ws2811_return_t.WS2811_SUCCESS) {
		printf("ws2811 error: %d\n", ret);
	}
}


extern(C) ws2811_t  strip = {
		freq: bandwidth,
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

	float sv[count][chans] = 0 ;
	float es[count][chans] = 0;

	printf("running at %d bit/s, %d pixels, for %0.2f fps. round %d\n", bandwidth, count, fps, round);
	check( ws2811_init(&strip) );
	auto leds = strip.channel[0].leds;

	StopWatch sw;
	sw.start();
	auto frametime = cast(int)(1000000000 / fps);
	auto tnext = sw.peek().nsecs + frametime;
	num h = 0.0;
	int frames = 0;
	num pixelangle = 360.0/count;

	float R,G,B;
	uint8_t rgbw[chans];
	enum float gamma = 2.4;


	while(keepRunning) {
		h += cwspeed;
		if(h>=360.) 
			h -= 360.0;
		for(int i = 0; i < count; i++) {
			auto offset = i * pixelangle * reps;
			Hsv2Rgb(&sv[i][0], &sv[i][1], &sv[i][2], h+offset, cwsat, cwvalue);
			for(int j=0; j<chans; j++) {
				auto withgamma = pow(sv[i][j], gamma);
				auto scaled = withgamma * 255.0;
				auto witherror = scaled + es[i][j];
				sv[i][j] = witherror;
				rgbw[j] = cast(uint8_t)sv[i][j];
				auto err = sv[i][j] - rgbw[j];
				if(round) 
					es[i][j] = (cast(int)(round * err))/cast(float)round;
				else
					es[i][j] = err;
			}
			leds[i] = rgb(rgbw[0], rgbw[1], rgbw[2], rgbw[3]);
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
