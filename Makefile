# Makefile for Poisson Process Simulation Project
# Authors: Paulo Fidalgo, Wagner Pedrosa
# Date: 2025-09-22
# Description: Builds the main simulation program with proper linking

CC = gcc
CFLAGS = -g -Wall -Wextra -std=c99 -O3 -I.
LDFLAGS = -lm

# Source files
SOURCES = main.c event/poison-process.c event/poison-event-driven.c models/linked-list.c poison/poison.c system/system.c call_center/call_center.c models/linked_list_call.c models/delay_array.c
OBJECTS = $(SOURCES:.c=.o)

all: main

# Compile object files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Link main executable
main: $(OBJECTS)
	$(CC) $(CFLAGS) -o main $(OBJECTS) $(LDFLAGS)

# Alternative pattern rule for single file compilation
%: %.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f main $(OBJECTS)
	find . -name "*.o" -type f -delete

.PHONY: clean all 