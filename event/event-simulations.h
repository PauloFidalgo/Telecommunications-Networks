/**
 * @file event-simulations.h
 * @author Paulo Fidalgo
 * @author Wagner Pedrosa
 * @brief Header file for Poisson process event simulation functions
 * @version 0.1
 * @date 2025-09-22
 *
 * @copyright Copyright (c) 2025
 *
 */

#ifndef EVENT_SIMULATIONS_H
#define EVENT_SIMULATIONS_H

#include "models/models.h"

Result poisson_event_driven_simulation(int lambda, int number_of_events);
Result poisson_process(int lambda, int number_of_events);

#endif // EVENT_SIMULATIONS_H
