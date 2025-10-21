#ifndef LINKED_LIST_H
#define LINKED_LIST_H

#include <stdbool.h>
typedef enum{
    GENERAL_PURPOSE,
    AREA_SPECIFIC,
} CALL_TYPE;

typedef struct general_call {
    bool is_generic_only;
    float anwser_time;
    bool blocked;
    bool delayed;
    float prediction_waiting;
    float actual_waiting;
} general_call;

typedef struct specific_call {
    float elapsed_time_after_gen;
} specific_call;

typedef struct call {
    CALL_TYPE type;
    struct general_call gen_call;
    struct specific_call spec_call;
} call;

typedef struct call_list
{
    int type;
    double time;
    struct call c;
    struct call_list *next;
} call_list;

call_list *__remove(call_list *pointer);
call_list *__add(call_list *pointer, int n_type, double n_time, call c);

#define ARRIVAL 1
#define DEPARTURE 2

#endif // LINKED_LIST_H
