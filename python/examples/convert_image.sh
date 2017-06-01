#!/usr/bin/env bash

WIDTH=288
OFFSETX=0
OFFSETY=0
convert "$1"  -crop 288x-1+$OFFSETX+$OFFSETY -resize 288x3600\! -gamma 0.4 "$1.leds.png"

