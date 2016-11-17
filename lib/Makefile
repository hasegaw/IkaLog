INCLUDE_DIR=/usr/local/Cellar/python3/3.4.3_2//Frameworks/Python.framework/Versions/3.4/include/python3.4m/

OPTS=-mfpu=neon -std=c11 -O2  -fPIC

all:
	gcc ${OPTS} ikamatcher2_neon_hal.c -o ikamatcher2_neon_hal.exec
	gcc ${OPTS} --shared ikamatcher2_neon_hal.c -o ikamatcher2_neon_hal.so
