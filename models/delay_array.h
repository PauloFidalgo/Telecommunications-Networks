#ifndef DELAY_ARRAY_H
#define DELAY_ARRAY_H

#include <stdlib.h>
#include <stdio.h>

typedef struct {
    double predicted;
    double actual;
} delay;

typedef struct {
    delay *data;
    int size;      
    int capacity; 
} delay_array;

void init_delay_array(delay_array *arr);
void add_delay(delay_array *arr, delay c);
void free_delay_array(delay_array *arr);

#endif /* DELAY_ARRAY_H */