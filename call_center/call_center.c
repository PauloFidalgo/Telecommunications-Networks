#include "call_center.h"

bool is_general_call(double gen_purpose_prob) {
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

double generate_exponential_duration(double min, double avg, bool has_max, double max) {
    double duration = 0;

    while (duration < min) {
        duration = min + next_poison(avg);
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
            config.gen_call_gen_only_config->gen_min_duration_s,
            config.gen_call_gen_only_config->gen_avg_duration_s,
            true,
            config.gen_call_gen_only_config->gen_max_duration_s);
    case AREA_SPECIFIC:
        return generate_general_purpose_area_specific_duration(*config.gen_call_specific_config);
    default:
        return 0.0;
    }
}

double generate_specific_duration(area_specific_config config) {
    return generate_exponential_duration(
        config.min_duration_s,
        config.avg_duration_s,
        false,
        0);
}

double running_avg(int n, double old_avg, double sample) {
    return (old_avg * ((n - 1.0) / n)) + (sample * (1.0 / n));
}

void handle_general_call_arrival(
    call_center_config config,
    int *general_call_delayed,
    int *general_opr_busy,
    int *in_queue_general_call,
    int *blocked_general_call,
    int *delayed_general_call,
    call_list **event_list,
    call_list **general_waiting_queue,
    double current_avg
) {
    if ((*general_opr_busy) < config.number_of_gen_opr) {
        (*general_opr_busy)++;

        CALL_TYPE type = (*event_list)->c.gen_call.is_generic_only ? GENERAL_PURPOSE : AREA_SPECIFIC;

        double duration = generate_general_purpose_duration(*config.general_p_config, type);

        call new_call;
        new_call.type = (*event_list)->c.type;
        new_call.gen_call.is_generic_only = (*event_list)->c.gen_call.is_generic_only;
        new_call.gen_call.prediction_waiting = 0.0;
        new_call.gen_call.anwser_time = (*event_list)->time;

        *event_list = _add(*event_list, DEPARTURE, (*event_list)->time + duration, new_call);

    } else {
        if ((*in_queue_general_call) >= config.length_gen_queue) {
            (*blocked_general_call)++;
        } else {
            (*general_call_delayed)++;
            (*delayed_general_call)++;
            
            call new_call;
            new_call.type = (*event_list)->c.type;
            new_call.gen_call.is_generic_only = (*event_list)->c.gen_call.is_generic_only;
            new_call.gen_call.prediction_waiting = (*in_queue_general_call) * current_avg;
            new_call.gen_call.anwser_time = 0.0;

            (*in_queue_general_call)++;
            (*general_waiting_queue) = _add(*general_waiting_queue, ARRIVAL, (*event_list)->time, new_call);
        }
    }
}

void handle_specific_call_arrival(
    call_center_config config,
    int *specific_opr_busy,
    call_list **event_list,
    call_list **specific_waiting_queue,
    double *total_elapsed_time_between_gen,
    double *total_specific
) {
    if ((*specific_opr_busy) < config.number_of_spec_opr) {
        double duration = generate_specific_duration(*config.area_spec_config);

        call new_call;
        new_call.type = (*event_list)->c.type;
        new_call.gen_call = (*event_list)->c.gen_call;
        (*total_elapsed_time_between_gen) += (*event_list)->time - (*event_list)->c.gen_call.anwser_time;
        (*total_specific)++;

        (*specific_opr_busy)++;
        *event_list = _add(
            *event_list,
            DEPARTURE,
            (*event_list)->time + duration,
            new_call);
    } else {
        *specific_waiting_queue = _add(
            *specific_waiting_queue,
            ARRIVAL,
            (*event_list)->time,
            (*event_list)->c);
    }
}

call_center_stats start_call_center(call_center_config config, int number_of_events) {
    int general_opr_busy = 0;
    int specific_opr_busy = 0;
    int general_call_delayed = 0;
    int in_queue_general_call = 0;
    int blocked_general_call = 0;
    int delayed_general_call = 0;
    int total = 0;
    int general_arrivals = 0;  
    double current_avg = 0.0;
    int current_count = 0;

    double total_elapsed_time_between_gen = 0.0;
    double total_specific = 0.0;

    call_list *event_list = NULL;
    call_list *general_waiting_queue = NULL;
    call_list *specific_waiting_queue = NULL;

    delay_array delays;
    init_delay_array(&delays);

    bool is_generic_only = is_general_call(config.general_purpose_ratio);

    struct call c;
    
    c.type = GENERAL_PURPOSE;
    struct general_call gen_call = {is_generic_only, 0.0, 0.0,};
    c.gen_call = gen_call;

    event_list = _add(event_list, ARRIVAL, 0.0, c);

    while (general_arrivals < number_of_events) {
        if (event_list->type == ARRIVAL) {
            if (event_list->c.type == AREA_SPECIFIC) {
                handle_specific_call_arrival(
                    config,
                    &specific_opr_busy,
                    &event_list,
                    &specific_waiting_queue,
                    &total_elapsed_time_between_gen,
                    &total_specific
                );
            } else {
                general_arrivals++; 
                total++;
                handle_general_call_arrival(
                    config,
                    &general_call_delayed,
                    &general_opr_busy,
                    &in_queue_general_call,
                    &blocked_general_call,
                    &delayed_general_call,
                    &event_list,
                    &general_waiting_queue,
                    current_avg,
                );
                
                is_generic_only = is_general_call(config.general_purpose_ratio);

                double tmp = next_poison(1.0 / config.arrival_rate);

                c.type = GENERAL_PURPOSE;
                struct general_call gen_call = {is_generic_only, 0.0, 0.0};
                c.gen_call = gen_call;

                event_list = _add(event_list, ARRIVAL, event_list->time + tmp, c);
            }

        } else if (event_list->type == DEPARTURE) {
            if (event_list->c.type == AREA_SPECIFIC) {
                if (specific_waiting_queue != NULL) {
                    double duration = generate_specific_duration(*config.area_spec_config);

                    total_elapsed_time_between_gen += event_list->time - specific_waiting_queue->c.gen_call.anwser_time;
                    total_specific++;

                    event_list = _add(event_list, DEPARTURE, event_list->time + duration, specific_waiting_queue->c);

                    specific_waiting_queue = _remove(specific_waiting_queue);
                } else {
                    specific_opr_busy--;
                }
            } else if (event_list->c.type == GENERAL_PURPOSE) {
                current_avg = running_avg(++current_count, current_avg, event_list->time - event_list->c.gen_call.anwser_time);

                if (general_waiting_queue != NULL) {
                    CALL_TYPE type = general_waiting_queue->c.gen_call.is_generic_only ? GENERAL_PURPOSE : AREA_SPECIFIC;

                    double duration = generate_general_purpose_duration(*config.general_p_config, type);

                    double waiting_time = event_list->time - general_waiting_queue->time;

                    delay d = {general_waiting_queue->c.gen_call.prediction_waiting, waiting_time};
                    add_delay(&delays, d);

                    general_waiting_queue->c.gen_call.anwser_time = event_list->time;

                    event_list = _add(event_list, DEPARTURE, event_list->time + duration, general_waiting_queue->c);
                    general_waiting_queue = _remove(general_waiting_queue);
                    in_queue_general_call--;
                } else {
                    general_opr_busy--;
                    in_queue_general_call = 0;
                }
                if (!event_list->c.gen_call.is_generic_only) {
                    event_list->c.type = AREA_SPECIFIC;
                    event_list = _add(event_list, ARRIVAL, event_list->time, event_list->c);
                }
            }
        }
        event_list = _remove(event_list);
    }


    double prob_delay = (double)delayed_general_call / (double)general_arrivals;
    double prob_blocked = (double)blocked_general_call / (double)general_arrivals;

    double total_actual_delay = 0.0;
    double total_abs_pred_error = 0.0;
    double total_rel_pred_error = 0.0;


    for (int i = 0; i < delays.size; i++) {
        total_actual_delay += delays.data[i].actual;
        total_abs_pred_error += fabs(delays.data[i].predicted - delays.data[i].actual);
        total_rel_pred_error += fabs(delays.data[i].predicted - delays.data[i].actual) / fabs(delays.data[i].actual);
    }

    call_center_stats result;
    general_purpose_stats general_result;
    general_result.prob_call_delayed = prob_delay;
    general_result.prob_call_lost = prob_blocked;
    general_result.avg_delay_of_calls = total_actual_delay / delays.size;
    general_result.avg_abs_prediction_error = total_abs_pred_error / delays.size;
    general_result.avg_rel_prediction_error = total_rel_pred_error / delays.size;
    general_result.delays = delays;

    area_specific_stats specific_result;
    specific_result.avg_answ_time = total_elapsed_time_between_gen / total_specific;

    result.general_p_stats = general_result;
    result.area_spec_stats = specific_result;

    return result;
}