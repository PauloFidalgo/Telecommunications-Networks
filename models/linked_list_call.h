#ifndef LINKED_LIST_H
#define LINKED_LIST_H
#include <stdbool.h>

typedef enum{
    GENERAL_PURPOSE,
    AREA_SPECIFIC,
} CALL_TYPE;

typedef struct general_call {
    bool is_generic_only;
    double anwser_time;
    double prediction_waiting;
} general_call;


typedef struct call {
    CALL_TYPE type;
    struct general_call gen_call;
} call;

typedef struct call_list
{
    int type;
    double time;
    struct call c;
    struct call_list *next;
} call_list;

call_list *_remove(call_list *pointer);
call_list *_add(call_list *pointer, int n_type, double n_time, call c);
void _print(call_list *pointer);

#define ARRIVAL 1
#define DEPARTURE 2

#endif // LINKED_LIST_H
