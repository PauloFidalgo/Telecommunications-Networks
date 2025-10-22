#include "delay_array.h"

void init_delay_array(delay_array *arr) {
    arr->size = 0;
    arr->capacity = 10; 
    arr->data = malloc(arr->capacity * sizeof(delay));
    if (!arr->data) {
        perror("malloc failed");
        exit(EXIT_FAILURE);
    }
}


void add_delay(delay_array *arr, delay c) {
    if (arr->size >= arr->capacity) {
        arr->capacity *= 2;
        delay *tmp = realloc(arr->data, arr->capacity * sizeof(delay));
        if (!tmp) {
            perror("realloc failed");
            exit(EXIT_FAILURE);
        }
        arr->data = tmp;
    }
    arr->data[arr->size++] = c;
}

void free_delay_array(delay_array *arr) {
    free(arr->data);
    arr->data = NULL;
    arr->size = arr->capacity = 0;
}