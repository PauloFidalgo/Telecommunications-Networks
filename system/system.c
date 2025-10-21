#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "../models/linked-list.h"
#include "../poison/poison.h"
#include "../models/models.h"

float erlang_b_system(int channels, int lambda, float avg_duration, int n_samples) {
    int busy = 0;
    float blocked = 0.0;
    float total = 0.0;

    list *event_list = NULL;

    event_list = __add(event_list, ARRIVAL, 0.0);

    while (total < n_samples)
    {
        if (event_list->type == ARRIVAL) {
            if (busy >= channels) {
                blocked++;
            } else {
                busy++;
                float dep = next_poison(avg_duration);
                event_list = __add(event_list, DEPARTURE, event_list->time + dep);
            }
            total++;
            double tmp = next_poison(1.0 / lambda);
            event_list = __add(event_list, ARRIVAL, event_list->time + tmp);
        } else if (event_list->type == DEPARTURE) {
            if (busy > 0) {
                busy--;
            }
        }
        event_list = __remove(event_list);
    }

    return (blocked > 0) ? blocked / total : 0.0;
}

ErlangCstat erlang_c_system(int channels, int lambda, float avg_duration, int n_samples, float delay_threshold) {
    int total = 0;
    int busy = 0;
    int higher_than_threshold = 0;
    float total_waiting_time = 0.0;
    int delayed = 0;

    list *event_list = NULL;
    list *waiting_queue = NULL;

    event_list = __add(event_list, ARRIVAL, 0.0);

    double delta = (1.0 / 5.0) * (1.0 / lambda);

    double v_max = 5.0 * (1.0 / lambda);

    int n = round(v_max / delta);

    int *histogram = calloc(n, sizeof(int)); 

    while (total < n_samples) {
        if (event_list->type == ARRIVAL) {
            total++;
            if (busy >= channels) {
                delayed++;
                waiting_queue = __add_fifo(waiting_queue, ARRIVAL, event_list->time);
            } else {
                busy++;
                float dep = next_poison(avg_duration);
                event_list = __add(event_list, DEPARTURE, event_list->time + dep);
            }
            double tmp = next_poison(1.0 / lambda);
            event_list = __add(event_list, ARRIVAL, event_list->time + tmp); 
    
        } else if (event_list->type == DEPARTURE){
            if (waiting_queue == NULL && busy > 0) {
                busy--;
            } else if (waiting_queue != NULL) {
                double elapsed_time = event_list->time - waiting_queue->time;

                total_waiting_time += elapsed_time;

                int bin_index = (int)(elapsed_time / delta);

                if (bin_index >= n - 1)
                {
                    bin_index = n - 1;
                }

                histogram[bin_index]++;

                if (elapsed_time >= delay_threshold) {
                    higher_than_threshold++;
                }

                float tmp = next_poison(avg_duration);
                event_list = __add(event_list, DEPARTURE, event_list->time + tmp);
                waiting_queue = __remove(waiting_queue);
            }
        }
        event_list = __remove(event_list);
    }

    ErlangCstat result;
    result.prob_pkt_delayed = (float)delayed / (float)total;
    result.avg_delay_all_pkt = (delayed > 0) ? total_waiting_time / (float)delayed : 0.0;
    result.prob_pkt_delayed_more_ax = (float)higher_than_threshold / (float)total;
    result.histogram = histogram;
    result.histogram_size = n;
    
    return result;
}

ErlangGenStat erlang_gen_system(int channels, int lambda, float avg_duration, int n_samples, float delay_threshold, int queue_capacity) {
    int total = 0;
    int busy = 0;
    int higher_than_threshold = 0;
    float total_waiting_time = 0.0;
    int delayed = 0;
    int blocked = 0;
    int in_queue = 0;

    list *event_list = NULL;
    list *waiting_queue = NULL;

    event_list = __add(event_list, ARRIVAL, 0.0);

    double delta = (1.0 / 5.0) * (1.0 / lambda);

    double v_max = 5.0 * (1.0 / lambda);

    int n = round(v_max / delta);

    int *histogram = calloc(n, sizeof(int)); 

    while (total < n_samples) {
        if (event_list->type == ARRIVAL) {
            total++;
            if (busy >= channels) {
                if (in_queue < queue_capacity) {
                    delayed++;
                    waiting_queue = __add_fifo(waiting_queue, ARRIVAL, event_list->time);
                    in_queue++;
                }
                else
                {
                    blocked++;
                }
            } else {
                busy++;
                float dep = next_poison(avg_duration);
                event_list = __add(event_list, DEPARTURE, event_list->time + dep);
            }
            double tmp = next_poison(1.0 / lambda);
            event_list = __add(event_list, ARRIVAL, event_list->time + tmp);
        } else if (event_list->type == DEPARTURE) {
            if (waiting_queue == NULL && busy > 0) {
                busy--;
                in_queue = 0;
            }
            else if (waiting_queue != NULL)
            {
                double elapsed_time = event_list->time - waiting_queue->time;

                total_waiting_time += elapsed_time;

                int bin_index = (int)(elapsed_time / delta);

                if (bin_index >= n - 1)
                {
                    bin_index = n - 1;
                }

                histogram[bin_index]++;

                if (elapsed_time >= delay_threshold) {
                    higher_than_threshold++;
                }

                float tmp = next_poison(avg_duration);
                event_list = __add(event_list, DEPARTURE, event_list->time + tmp);
                waiting_queue = __remove(waiting_queue);
                in_queue--;
            }
        }
        event_list = __remove(event_list);
    }

    ErlangGenStat result;
    result.prob_pkt_delayed = (float)delayed / (float)total;
    result.avg_delay_all_pkt = (delayed > 0) ? total_waiting_time / (float)delayed : 0.0;
    result.prob_pkt_delayed_more_ax = (float)higher_than_threshold / (float)total;
    result.block_probability = (float)blocked / (float)total;
    result.histogram = histogram;
    result.histogram_size = n;
    
    return result;
}