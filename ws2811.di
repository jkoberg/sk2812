module ws2811;

import std.stdint;
import rpihw;
import pwm;

extern (C) {

alias ws2811_led_t = uint32_t;

struct ws2811_device {}

struct ws2811_channel_t {
	int gpionum;
	int invert;
	int count;
	int strip_type;
	ws2811_led_t *leds;
	uint8_t brightness;
	uint8_t wshift;
	uint8_t rshift;
	uint8_t gshift;
	uint8_t bshift;
}

struct ws2811_t {
	ws2811_device *device;
	const rpi_hw_t *rpi_hw;
	uint32_t freq;
	int dmanum;
	ws2811_channel_t[2] channel;
}


ws2811_return_t ws2811_init  (ws2811_t *ws2811);
void            ws2811_fini  (ws2811_t *ws2811);
ws2811_return_t ws2811_render(ws2811_t *ws2811);
ws2811_return_t ws2811_wait  (ws2811_t *ws2811);
const char * ws2811_get_return_t_str(const ws2811_return_t state);


enum auto WS2811_TARGET_FREQ                     =  800000;
enum auto WS2811_STRIP_RGB                       =  0x00100800;
enum auto WS2811_STRIP_RBG                       =  0x00100008;
enum auto WS2811_STRIP_GRB                       =  0x00081000;
enum auto WS2811_STRIP_GBR                       =  0x00080010;
enum auto WS2811_STRIP_BRG                       =  0x00001008;
enum auto WS2811_STRIP_BGR                       =  0x00000810;
enum auto WS2812_STRIP                           =  WS2811_STRIP_GRB;
enum auto SK6812_STRIP_RGBW                      =  0x18100800;
enum auto SK6812_STRIP_RBGW                      =  0x18100008;
enum auto SK6812_STRIP_GRBW                      =  0x18081000;
enum auto SK6812_STRIP_GBRW                      =  0x18080010;
enum auto SK6812_STRIP_BRGW                      =  0x18001008;
enum auto SK6812_STRIP_BGRW                      =  0x18000810;
enum auto SK6812_SHIFT_WMASK                     =  0xf0000000;
enum auto SK6812_STRIP                           =  WS2811_STRIP_GRB;
enum auto SK6812W_STRIP                          =  SK6812_STRIP_GRBW;


enum ws2811_return_t {
 WS2811_SUCCESS = 0,
 WS2811_ERROR_GENERIC = -1,
 WS2811_ERROR_OUT_OF_MEMORY = -2,
 WS2811_ERROR_HW_NOT_SUPPORTED = -3,
 WS2811_ERROR_MEM_LOCK = -4,
 WS2811_ERROR_MMAP = -5,
 WS2811_ERROR_MAP_REGISTERS = -6,
 WS2811_ERROR_GPIO_INIT = -7,
 WS2811_ERROR_PWM_SETUP = -8,
 WS2811_ERROR_MAILBOX_DEVICE = -9,
 WS2811_ERROR_DMA = -10,
 WS2811_ERROR_ILLEGAL_GPIO = -11,
 WS2811_ERROR_PCM_SETUP = -12,
 WS2811_ERROR_SPI_SETUP = -13,
 WS2811_ERROR_SPI_TRANSFER = -14,
}
}
