
module leds;

import std.stdio;
import std.stdint;
import core.stdc.stdlib;
import core.thread;

import ws2811;


void check(ws2811_return_t ret) {
	if(ret != ws2811_return_t.WS2811_SUCCESS) {
		printf("ws2811 error: %d\n", ret);
	}
}

ws2811_led_t rgb(uint8_t r, uint8_t g, uint8_t b, uint8_t w=0) {
	return (w << 24) + (r << 16) + (g << 8) + b;
}

void render(ws2811_t* strip) {
	check(ws2811_render(strip));
	check(ws2811_wait(strip));
}

void main() {
	enum int count = 288;
	extern(C) ws2811_t strip = {
		freq: 800000,
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

	check(ws2811_init(&strip));

	auto leds = strip.channel[0].leds;

	leds[0..count] = rgb(255,0,0);
	render(&strip);

	leds[0..count] = rgb(0,255,0);
	render(&strip);

	leds[0..count] = rgb(0,0,255);
	render(&strip);

	leds[0..count] = rgb(0,0,0,255);
	render(&strip);

	leds[0..count] = rgb(0,0,0);
	render(&strip);

	ws2811_fini(&strip);

}
