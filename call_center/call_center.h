#ifndef CALL_CENTER_H
#define CALL_CENTER_H

// ------------------- INPUT MODELS ------------------- //
typedef struct {
    float gen_min_duration_s;
    float gen_avg_duration_s;
    float gen_max_duration_s;
} generic_call_gen_only_config;

typedef struct {
    float spec_min_duration_s;
    float spec_avg_duration_s;
    float spec_std_duration_s;
    float spec_max_duration_s;
} generic_call_specific_config;

typedef struct {
    union {
        generic_call_gen_only_config gen_call_gen_only_config;
        generic_call_specific_config gen_call_specific_config;
    } gen_call_config;
} general_purpose_config;

typedef struct {
    float min_duration_s;
    float avg_duration_s;
} area_specific_config;

typedef struct {
    int number_of_gen_opr;
    int number_of_spec_opr;
    int length_gen_queue;
    float arrival_rate;
    float general_purpose_ratio;
    general_purpose_config *general_p_config;
    area_specific_config *area_spec_config;
} call_center_config;

// ------------------- OUTPUT MODELS ------------------- //

typedef struct {
    float prob_call_delayed;
    float prob_call_lost;
    float avg_delay_of_calls;
    float avg_abs_prediction_error;
    float avg_rel_prediction_error;
} general_purpose_stats;

typedef struct {
    float avg_answ_time;
} area_specific_stats;

typedef struct {
    general_purpose_stats *general_p_stats;
    area_specific_stats *area_spec_stats;
} call_center_stats;

void start_call_center(call_center_config config, int number_of_events);

#endif // CALL_CENTER_H