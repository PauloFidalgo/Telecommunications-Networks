#ifndef CALL_CENTER_H
#define CALL_CENTER_H

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "../poison/poison.h"
#define M_PI 3.1415926535
#include "../models/delay_array.h"
#include "../models/linked_list_call.h"

// ------------------- INPUT MODELS ------------------- //
typedef struct {
    double gen_min_duration_s;
    double gen_avg_duration_s;
    double gen_max_duration_s;
} generic_call_gen_only_config;

typedef struct {
    double spec_min_duration_s;
    double spec_avg_duration_s;
    double spec_std_duration_s;
    double spec_max_duration_s;
} generic_call_specific_config;

typedef struct {
    generic_call_gen_only_config *gen_call_gen_only_config;
    generic_call_specific_config *gen_call_specific_config;
} general_purpose_config;

typedef struct {
    double min_duration_s;
    double avg_duration_s;
} area_specific_config;

typedef struct {
    int number_of_gen_opr;
    int number_of_spec_opr;
    int length_gen_queue;
    double arrival_rate;
    double general_purpose_ratio;
    general_purpose_config *general_p_config;
    area_specific_config *area_spec_config;
} call_center_config;

// ------------------- OUTPUT MODELS ------------------- //

typedef struct {
    double prob_call_delayed;
    double prob_call_lost;
    double avg_delay_of_calls;
    double avg_abs_prediction_error;
    double avg_rel_prediction_error;
    delay_array delays;
} general_purpose_stats;

typedef struct {
    double avg_answ_time;
} area_specific_stats;

typedef struct {
    general_purpose_stats general_p_stats;
    area_specific_stats area_spec_stats;
} call_center_stats;

call_center_stats start_call_center(call_center_config config, int number_of_events);

#endif // CALL_CENTER_H