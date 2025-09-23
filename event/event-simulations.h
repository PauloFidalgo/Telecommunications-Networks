#ifndef EVENT_SIMULATIONS_H
#define EVENT_SIMULATIONS_H

#include "models/models.h"

Result poison_event_driven_simulation(int lambda, int number_of_events);
Result poison_process(int lambda, int number_of_events);

#endif // EVENT_SIMULATIONS_H
