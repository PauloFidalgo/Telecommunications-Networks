#include <stdio.h>
#include <stdlib.h>
#include "linked_list_call.h"

// Function that removes the first element of the linked list
call_list *__remove(call_list *pointer)
{
    call_list *lp = (call_list *)pointer->next;
    free(pointer);
    return lp;
}

// Function that adds a new element to the list, sorting the list in chronological order
call_list *__add(call_list *pointer, int n_type, double n_time, call c)
{
    call_list *lp = pointer;
    call_list *p_aux, *p_next;
    if (pointer == NULL)
    {
        pointer = (call_list *)malloc(sizeof(call_list));
        pointer->next = NULL;
        pointer->type = n_type;
        pointer->time = n_time;
        pointer->c = c;
        return pointer;
    }
    else
    {
        if (pointer->time > n_time)
        {
            p_aux = (call_list *)malloc(sizeof(call_list));
            p_aux->type = n_type;
            p_aux->time = n_time;
            p_aux->next = (struct call_list *)pointer;
            p_aux->c = c;
            return p_aux;
        }

        p_next = (call_list *)pointer->next;

        while (pointer != NULL)
        {
            if ((p_next == NULL) || ((p_next->time) > n_time))
                break;
            pointer = (call_list *)pointer->next;
            p_next = (call_list *)pointer->next;
        }
        p_aux = (call_list *)pointer->next;
        pointer->next = (struct call_list *)malloc(sizeof(call_list));
        pointer = (call_list *)pointer->next;
        if (p_aux != NULL)
            pointer->next = (struct call_list *)p_aux;
        else
            pointer->next = NULL;
        pointer->type = n_type;
        pointer->time = n_time;
        pointer->c = c;
        return lp;
    }
}
