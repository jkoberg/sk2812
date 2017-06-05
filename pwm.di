
module pwm;

import std.stdint;

extern(C) {

struct pwm_t {
	align(4):
	uint32_t ctl;
	uint32_t sta;
	uint32_t dmac;
	uint32_t resvd_0x0c;
	uint32_t rng1;
	uint32_t dat1;
	uint32_t fif1;
	uint32_t resvd_0x1c;
	uint32_t rng2;
	uint32_t dat2;
}

struct pwm_pin_table_t {
	int pinnum;
	int altnum;
}

struct pwm_pin_tables_t {
	const int count;
	const pwm_pin_table_t *pins;
}


int pwm_pin_alt(int chan, int pinnum);

auto enum RPI_PWM_CHANNELS                       =  2;
auto enum RPI_PWM_CTL_MSEN2                      =  (1 << 15);
auto enum RPI_PWM_CTL_USEF2                      =  (1 << 13);
auto enum RPI_PWM_CTL_POLA2                      =  (1 << 12);
auto enum RPI_PWM_CTL_SBIT2                      =  (1 << 11);
auto enum RPI_PWM_CTL_RPTL2                      =  (1 << 10);
auto enum RPI_PWM_CTL_MODE2                      =  (1 << 9);
auto enum RPI_PWM_CTL_PWEN2                      =  (1 << 8);
auto enum RPI_PWM_CTL_MSEN1                      =  (1 << 7);
auto enum RPI_PWM_CTL_CLRF1                      =  (1 << 6);
auto enum RPI_PWM_CTL_USEF1                      =  (1 << 5);
auto enum RPI_PWM_CTL_POLA1                      =  (1 << 4);
auto enum RPI_PWM_CTL_SBIT1                      =  (1 << 3);
auto enum RPI_PWM_CTL_RPTL1                      =  (1 << 2);
auto enum RPI_PWM_CTL_MODE1                      =  (1 << 1);
auto enum RPI_PWM_CTL_PWEN1                      =  (1 << 0);
auto enum RPI_PWM_STA_STA4                       =  (1 << 12);
auto enum RPI_PWM_STA_STA3                       =  (1 << 11);
auto enum RPI_PWM_STA_STA2                       =  (1 << 10);
auto enum RPI_PWM_STA_STA1                       =  (1 << 9);
auto enum RPI_PWM_STA_BERR                       =  (1 << 8);
auto enum RPI_PWM_STA_GAP04                      =  (1 << 7);
auto enum RPI_PWM_STA_GAP03                      =  (1 << 6);
auto enum RPI_PWM_STA_GAP02                      =  (1 << 5);
auto enum RPI_PWM_STA_GAP01                      =  (1 << 4);
auto enum RPI_PWM_STA_RERR1                      =  (1 << 3);
auto enum RPI_PWM_STA_WERR1                      =  (1 << 2);
auto enum RPI_PWM_STA_EMPT1                      =  (1 << 1);
auto enum RPI_PWM_STA_FULL1                      =  (1 << 0);
auto enum RPI_PWM_DMAC_ENAB                      =  (1 << 31);
int RPI_PWM_DMAC_PANIC(int val)                { return   ((val & 0xff) << 8); }
int RPI_PWM_DMAC_DREQ(int val)                 { return  ((val & 0xff) << 0); }
auto enum PWM_OFFSET = 0x0020c0000;
auto enum PWM_PERIPH_PHYS = 0x7e20c000;


}
