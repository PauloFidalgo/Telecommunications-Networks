#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../models/linked-list.h"
#include "../poison/poison.h"
#include "../models/models.h"

Result poison_process(int lambda, int number_of_events)
{
    list *event_list = NULL;

    double sum = 0.0;
    double delta_histogram = (1.0 / 5.0) * (1.0 / lambda);
    double v_max = 5.0 * (1.0 / lambda);

    // Number of hist bins
    int n = round(v_max / delta_histogram);

    // This delta is the step in the process
    double delta = 0.000001;
    double current_time = 0.0;

    int generated_events = 0;

    int *histogram = calloc(n, sizeof(int));

    double last_event = 0.0;

    while (generated_events < number_of_events)
    {
        double u = (double)rand() / (double)RAND_MAX;

        if (u <= lambda * delta)
        {
            sum += current_time - last_event;

            // Event Arrived
            int bin_index = (int)((current_time - last_event) / delta_histogram);

            last_event = current_time;

            if (bin_index >= n - 1)
            {
                bin_index = n - 1;
            }

            histogram[bin_index]++;

            event_list = __add(event_list, ARRIVAL, current_time);
            event_list = __remove(event_list);
            generated_events++;
        }

        current_time += delta;
    }

    Result res;
    res.average = sum / number_of_events;
    res.theoretical_average = 1.0 / lambda;
    res.histogram = histogram;
    res.histogram_size = n;

    return res;
}