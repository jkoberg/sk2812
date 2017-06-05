module rpihw;
import std.stdint;

extern(C) {


enum auto RPI_HWVER_TYPE_UNKNOWN = 0;
enum auto RPI_HWVER_TYPE_PI1 = 1;
enum auto RPI_HWVER_TYPE_PI2 = 2;

struct rpi_hw_t {
	uint32_t type;
	uint32_t hwver;
	uint32_t periph_base;
	uint32_t videocore_base;
	char *desc;
}

const rpi_hw_t* rpi_hw_detect();

}
