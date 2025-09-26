/**
 * @file poison-event-driven.c
 * @author Paulo Fidalgo
 * @author Wagner Pedrosa
 * @brief This file implements event-driven Poisson process simulation
 * @version 0.1
 * @date 2025-09-22
 *
 * @copyright Copyright (c) 2025
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../models/linked-list.h"
#include "../poison/poison.h"
#include "../models/models.h"

Result poison_event_driven_simulation(int lambda, int number_of_events)
{
    list *event_list = NULL;

    event_list = __add(event_list, ARRIVAL, 0.0);

    double sum = 0.0;
    double delta = (1.0 / 5.0) * (1.0 / lambda);

    double v_max = 5.0 * (1.0 / lambda);

    int n = round(v_max / delta);

    int *histogram = calloc(n, sizeof(int));

    for (int i = 0; i < number_of_events; i++)
    {
        double c = next_poison(lambda);
        sum += c;

        int bin_index = (int)(c / delta);

        if (bin_index >= n - 1)
        {
            bin_index = n - 1;
        }

        histogram[bin_index]++;

        double next_time = event_list->time + c;
        event_list = __add(event_list, ARRIVAL, next_time);

        event_list = __remove(event_list);
    }

    Result res;
    res.average = sum / number_of_events;
    res.theoretical_average = 1.0 / lambda;
    res.histogram = histogram;
    res.histogram_size = n;

    return res;
}