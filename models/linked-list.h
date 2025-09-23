#ifndef LINKED_LIST_H
#define LINKED_LIST_H

typedef struct list
{
    int type;
    double time;
    struct list *next;
} list;

list *__remove(list *pointer);
list *__add(list *pointer, int n_type, double n_time);
void __print(list *pointer);

#define ARRIVAL 1
#define DEPARTURE 2

#endif // LINKED_LIST_H
