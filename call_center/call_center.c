#include "call-center.h"
#include <stdlib.h>
#include <math.h>
#include "../poison/poison.h"
#include "../models/linked_list_call.h"


// Function to check the next call is General Purpose or Area Specific
bool is_general_call(float gen_purpose_prob) {
    double u = (double)rand() / (double)RAND_MAX;

    return u <= gen_purpose_prob;
}

double box_muller() {
    double u1 = (double)rand() / (double)RAND_MAX;
    double u2 = (double)rand() / (double)RAND_MAX;

    double theta = 2 * u1 * M_PI;
    double r = sqrt(-2 * log(u2));

    return r * cos(theta);
}

double generate_general_purpose_area_specific_duration(generic_call_specific_config config) {
    double duration = 0;
    
    while (duration < config.spec_min_duration_s) {
        double rv = box_muller();
        duration = rv * config.spec_std_duration_s + config.spec_avg_duration_s;
    }

    return (duration > config.spec_max_duration_s) ? config.spec_max_duration_s : duration;
}


double generate_exponential_duration(float min, float avg, bool has_max, float max) {
    double duration = 0;

    while (duration < min) {
        duration = 1 + next_poison(1.0 / avg);
    }

    if (has_max) {
            return (duration > max) ? max : duration;
    }

    return duration;
}

double generate_general_purpose_duration(general_purpose_config config, CALL_TYPE type) {
    switch (type) {
        case GENERAL_PURPOSE:
            return generate_exponential_duration(
                config.gen_call_config.gen_min_duration_s, 
                config.gen_call_config.gen_avg_duration_s, 
                true, 
                config.gen_call_config.gen_max_duration_s,
            );
        case AREA_SPECIFIC:
            return generate_general_purpose_area_specific_duration(config.gen_call_config);
    }
}

double generate_specific_duration(area_specific_config config) {
    return generate_exponential_duration(
                config.min_duration_s, 
                config.avg_duration_s, 
                false, 
                0,
            ); 
}

void handle_general_call_arrival(
    call_center_config config, 
    int *general_call_delayed, 
    int *general_opr_busy, 
    int *in_queue_general_call, 
    int *blocked_general_call, 
    call_list *event_list, 
    call_list *general_waiting_queue,
) {
    if ((*general_opr_busy) < config.number_of_gen_opr) {
        // Está livre, vou gerar a departure da chamada
        (*general_opr_busy)++;

        struct CALL_TYPE type = event_list->c.gen_call.is_generic_only ? GENERAL_PURPOSE : AREA_SPECIFIC;

        double duration = generate_general_purpose_duration(config.general_p_config, type);

        event_list->c.gen_call.anwser_time = event_list->time;
        if (event_list->c.gen_call.is_generic_only) {
            calls[calls_idx++] = event_list->c;
        }
        
        event_list = __add(event_list, DEPARTURE, event_list->time + duration, event_list->c);
    } else {
        (*general_call_delayed)++;
        if ((*in_queue_general_call) >= config.length_gen_queue) {
            // nao tenho capacidade -> blocked
            (*blocked_general_call)++;
            event_list->c.gen_call.blocked = true;
        } else {
            // tenho capacidade -> entra na queue
            event_list->c.gen_call.delayed = true;
            event_list->c.gen_call.prediction_waiting = 100000.0; ///////// DEPOIS METER MOVING AVG

            general_waiting_queue = __add(general_waiting_queue, ARRIVAL, event_list->time, event_list->c);
            (*delayed_general_call)++;
            (*in_queue_general_call)++;
        }
    }
}

void handle_specific_call_arrival(
    call_center_config config,
    int *specific_opr_busy,
    call_list *event_list, 
    call_list *specific_waiting_queue,
) {
    if ((*specific_opr_busy) < config.number_of_spec_opr) {
        double duration = generate_specific_duration(config.area_spec_config);

        event_list->c.spec_call.elapsed_time_after_gen = event_list->time - event_list->c.gen_call.anwser_time;

        calls[calls_idx++] = event_list->c;
        (*specific_opr_busy)++;
        event_list = __add(event_list, DEPARTURE, event_list->time + duration, event_list->c);
    } else {
        specific_waiting_queue = __add(specific_waiting_queue, ARRIVAL, event_list->time, event_list->c);
    }
}

void start_call_center(call_center_config config, int number_of_events) {
    int general_opr_busy = 0;
    int specific_opr_busy = 0;
    int general_call_delayed = 0;
    int in_queue_general_call = 0;
    int blocked_general_call = 0;
    int delayed_general_call = 0;
    int total = 0;

    call_list *event_list = NULL;
    call_list *general_waiting_queue = NULL;
    call_list *specific_waiting_queue = NULL;

    struct call calls[number_of_events];
    int calls_idx = 0;

    bool is_generic_only = is_general_call(config.general_purpose_ratio);

    struct call c;

    c.type = GENERAL_PURPOSE;
    struct general_call gen_call = {is_generic_only, 0.0, false, false, 0.0, 0.0, 0.0};
    c.gen_call = gen_call;

    event_list = __add(event_list, ARRIVAL, 0.0, c);

    while (total < number_of_events) {
        if (event_list->type == ARRIVAL) {
            total++;
            if (event_list->c.type == AREA_SPECIFIC) {
                handle_specific_call_arrival(
                    config,
                    &specific_opr_busy,
                    event_list,
                    specific_waiting_queue,
                );
            } else {
                handle_general_call_arrival(
                    config,
                    &general_call_delayed,
                    &general_opr_busy,
                    &in_queue_general_call,
                    &blocked_general_call,
                    event_list,
                    general_waiting_queue,
                );
            }
            
            is_generic_only = is_general_call(config.general_purpose_ratio);
            double tmp = next_poison(1.0 / config.arrival_rate);

            c.type = GENERAL_PURPOSE;
            struct general_call gen_call = {is_generic_only, 0.0, false, false, 0.0, 0.0, 0.0};
            c.gen_call = gen_call;

            event_list = __add(event_list, ARRIVAL, event_list->time + tmp, c);

        } else if (event_list->type == DEPARTURE) {
            if (event_list->c.type == AREA_SPECIFIC) {
                if (specific_waiting_queue != NULL) {
                    double duration = generate_specific_duration(config.area_spec_config);

                    specific_waiting_queue->c.spec_call.elapsed_time_after_gen = event_list->time - specific_waiting_queue->c.gen_call.anwser_time;

                    calls[calls_idx++] = specific_waiting_queue->c;

                    event_list = __add(event_list, DEPARTURE, event_list->time + duration, event_list->c);
                    specific_waiting_queue = __remove(specific_waiting_queue);
                } else {
                    specific_opr_busy--;
                }
            } else if (event_list->c.type == GENERAL_PURPOSE) {
                if (general_waiting_queue != NULL) {
                    struct CALL_TYPE type = general_waiting_queue->c.gen_call.is_generic_only ? GENERAL_PURPOSE : AREA_SPECIFIC;

                    double duration = generate_general_purpose_duration(config.general_p_config, type);

                    general_waiting_queue->c.gen_call.anwser_time = event_list->time;

                    if (general_waiting_queue->c.gen_call.is_generic_only) {
                        calls[calls_idx++] = general_waiting_queue->c;
                    }
                    
                    event_list = __add(event_list, DEPARTURE, event_list->time + duration, event_list->c);
                    general_waiting_queue = __remove(general_waiting_queue);
                    in_queue_general_call--;
                } else {
                    general_opr_busy--;
                    in_queue_general_call = 0;
                }
                if (!event_list->c.gen_call.is_generic_only) {
                    event_list->c.type = AREA_SPECIFIC;
                    event_list = __add(event_list, ARRIVAL, event_list->time, event_list->c);
                }
            }
        }
        event_list = __remove(event_list);
    }


    for (int i = 0; i < number_of_events; i++) {
        printf("Call %d, type: %X\n", i + 1, calls[i].type);
    }
}