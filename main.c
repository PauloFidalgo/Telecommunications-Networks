#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include "call_center/call_center.h"
#include "models/delay_array.h"
#include "constants.h"
#include "optimize_param.h"

bool is_valid_result(call_center_stats stats, double target_delayed, double target_lost, double target_avg_delay, double target_total_delay) {
    return stats.general_p_stats.prob_call_delayed <= target_delayed &&
            stats.general_p_stats.prob_call_lost <= target_lost &&
            stats.general_p_stats.avg_delay_of_calls <= target_avg_delay && 
            stats.area_spec_stats.avg_answ_time <= target_total_delay;
}

void initialize_config(call_center_config *config, 
                       generic_call_gen_only_config *gen_call_only,
                       generic_call_specific_config *gen_call_specific_config,
                       general_purpose_config *general_p_cfg,
                       area_specific_config *area_spec_config) {
    config->arrival_rate = ARRIVAL_RATE;
    config->general_purpose_ratio = GENERAL_PURPOSE_RATIO;
    
    gen_call_only->gen_min_duration_s = GEN_CALL_MIN_DURATION_S;
    gen_call_only->gen_avg_duration_s = GEN_CALL_AVG_DURATION_S;
    gen_call_only->gen_max_duration_s = GEN_CALL_MAX_DURATION_S;
    
    gen_call_specific_config->spec_min_duration_s = SPEC_MIN_DURATION_S;
    gen_call_specific_config->spec_avg_duration_s = SPEC_AVG_DURATION_S;
    gen_call_specific_config->spec_std_duration_s = SPEC_STD_DURATION_S;
    gen_call_specific_config->spec_max_duration_s = SPEC_MAX_DURATION_S;
    
    general_p_cfg->gen_call_gen_only_config = gen_call_only;
    general_p_cfg->gen_call_specific_config = gen_call_specific_config;
    
    config->general_p_config = general_p_cfg;
    
    area_spec_config->min_duration_s = AREA_SPEC_MIN_DURATION_S;
    area_spec_config->avg_duration_s = AREA_SPEC_AVG_DURATION_S;
    config->area_spec_config = area_spec_config;
}

void run_optimization() {
    printf("Starting MSE-based optimization...\n");
    printf("Using fixed random seed: %d (reset before each configuration)\n", RANDOM_SEED);
    
    call_center_config config;
    generic_call_gen_only_config gen_call_only;
    generic_call_specific_config gen_call_specific_config;
    general_purpose_config general_p_cfg;
    area_specific_config area_spec_config;
    
    initialize_config(&config, &gen_call_only, &gen_call_specific_config, 
                     &general_p_cfg, &area_spec_config);
    
    double best_mse = 1e9;
    int best_gen = 0, best_spec = 0, best_queue = 0;
    call_center_stats best_stats;
    
    int count = 0;
    int total = (MAX_GEN_OPR - MIN_GEN_OPR + 1) * (MAX_SPEC_OPR - MIN_SPEC_OPR + 1) * (MAX_QUEUE_LEN - MIN_QUEUE_LEN + 1);
    
    for (int gen_opr = MIN_GEN_OPR; gen_opr <= MAX_GEN_OPR; gen_opr++) {
        for (int spec_opr = MIN_SPEC_OPR; spec_opr <= MAX_SPEC_OPR; spec_opr++) {
            for (int queue_len = MIN_QUEUE_LEN; queue_len <= MAX_QUEUE_LEN; queue_len++) {
                count++;
                
                if (RANDOM_SEED == 0) {
                    srand(time(NULL));
                } else {
                    srand(RANDOM_SEED);
                }
                
                config.number_of_gen_opr = gen_opr;
                config.number_of_spec_opr = spec_opr;
                config.length_gen_queue = queue_len;
                
                call_center_stats stats = start_call_center(config, NUMBER_OF_EVENTS);

                if (is_valid_result(stats, TARGET_PROB_DELAYED, TARGET_PROB_LOST, TARGET_AVG_DELAY_S, TARGET_TOTAL_DELAY_S)) {
                    double normalized_mse_delayed = pow((stats.general_p_stats.prob_call_delayed - TARGET_PROB_DELAYED) / TARGET_PROB_DELAYED, 2);
                    double normalized_mse_lost = pow((stats.general_p_stats.prob_call_lost - TARGET_PROB_LOST) / TARGET_PROB_LOST, 2);
                    double normalized_mse_avg_delay = pow((stats.general_p_stats.avg_delay_of_calls - TARGET_AVG_DELAY_S) / TARGET_AVG_DELAY_S, 2);
                    double normalized_mse_total_delay = pow((stats.area_spec_stats.avg_answ_time - TARGET_TOTAL_DELAY_S) / TARGET_TOTAL_DELAY_S, 2);
                    
                    double total_mse = normalized_mse_delayed + normalized_mse_lost + normalized_mse_avg_delay + normalized_mse_total_delay;
                    
                    if (total_mse < best_mse) {
                        // Free old best_stats delay array if it exists
                        if (best_mse < 1e9) {
                            free_delay_array(&best_stats.general_p_stats.delays);
                        }
                        
                        best_mse = total_mse;
                        best_gen = gen_opr;
                        best_spec = spec_opr;
                        best_queue = queue_len;
                        best_stats = stats;
                        
                        printf("[%d/%d] NEW BEST: gen=%d, spec=%d, queue=%d | MSE=%.6f\n",
                            count, total, gen_opr, spec_opr, queue_len, total_mse);
                        printf("  Delayed: %.4f (target: %.2f)\n", stats.general_p_stats.prob_call_delayed, TARGET_PROB_DELAYED);
                        printf("  Lost: %.4f (target: %.2f)\n", stats.general_p_stats.prob_call_lost, TARGET_PROB_LOST);
                        printf("  Avg delay in General System: %.2f (target: %.2f)\n", stats.general_p_stats.avg_delay_of_calls, TARGET_AVG_DELAY_S);
                        printf("  Avg time between General Arrival and Specific Handling: %.2f (target: %.2f)\n\n", stats.area_spec_stats.avg_answ_time, TARGET_TOTAL_DELAY_S);
                    } else {
                        // Free delay array for non-best stats
                        free_delay_array(&stats.general_p_stats.delays);
                    }
                }
                
                if (count % 10 == 0 || count == total) {
                    printf("\rProgress: %d/%d (%.1f%%)    ", count, total, 100.0 * count / total);
                    fflush(stdout);
                }
                
            }
        }
    }
    
    printf("\n");
    
    printf("\n========================================\n");
    printf("OPTIMIZATION COMPLETE\n");
    printf("========================================\n\n");
    printf("Best configuration found:\n");
    printf("  General operators: %d\n", best_gen);
    printf("  Specialist operators: %d\n", best_spec);
    printf("  Queue length: %d\n", best_queue);
    printf("  Total MSE: %.6f\n\n", best_mse);
    
    printf("Performance:\n");
    printf("  Prob. delayed: %.4f (target: %.2f)\n", best_stats.general_p_stats.prob_call_delayed, TARGET_PROB_DELAYED);
    printf("  Prob. lost: %.4f (target: %.2f)\n", best_stats.general_p_stats.prob_call_lost, TARGET_PROB_LOST);
    printf("  Avg delay in General System: %.2f s (target: %.2f s)\n", best_stats.general_p_stats.avg_delay_of_calls, TARGET_AVG_DELAY_S);
    printf("  Avg time between General Arrival and Specific Handling: %.2f s (target: %.2f s)\n", best_stats.area_spec_stats.avg_answ_time, TARGET_TOTAL_DELAY_S);
}

void run_simulation(int gen_opr, int spec_opr, int queue_len) {
    // Set random seed
    if (RANDOM_SEED == 0) {
        srand(time(NULL));
        printf("Using time-based random seed\n\n");
    } else {
        srand(RANDOM_SEED);
        printf("Using fixed random seed: %d\n\n", RANDOM_SEED);
    }
    
    printf("Running simulation with configuration:\n");
    printf("  General operators: %d\n", gen_opr);
    printf("  Specialist operators: %d\n", spec_opr);
    printf("  Queue length: %d\n", queue_len);
    printf("  Arrival rate: %.2f calls/hour\n", ARRIVAL_RATE_PER_HOUR);
    printf("  General purpose ratio: %.2f\n\n", GENERAL_PURPOSE_RATIO);
    
    call_center_config config;
    generic_call_gen_only_config gen_call_only;
    generic_call_specific_config gen_call_specific_config;
    general_purpose_config general_p_cfg;
    area_specific_config area_spec_config;
    
    initialize_config(&config, &gen_call_only, &gen_call_specific_config, 
                     &general_p_cfg, &area_spec_config);
    
    config.number_of_gen_opr = gen_opr;
    config.number_of_spec_opr = spec_opr;
    config.length_gen_queue = queue_len;
    
    call_center_stats stats = start_call_center(config, NUMBER_OF_EVENTS);
    
    printf("========================================\n");
    printf("SIMULATION RESULTS\n");
    printf("========================================\n\n");
    
    printf("General Purpose System:\n");
    printf("  Prob. General call delayed: %.4f\n", stats.general_p_stats.prob_call_delayed);
    printf("  Prob. General call lost: %.4f\n", stats.general_p_stats.prob_call_lost);
    printf("  Avg delay in General System: %.2f s\n", stats.general_p_stats.avg_delay_of_calls);
    printf("  Avg absolute prediction error: %.2f s\n", stats.general_p_stats.avg_abs_prediction_error);
    printf("  Avg relative prediction error: %.4f\n\n", stats.general_p_stats.avg_rel_prediction_error);
    
    printf("Area-Specific System:\n");
    printf("  Avg time between General Arrival and Specific Handling: %.2f s\n", stats.area_spec_stats.avg_answ_time);
    
    // Save delay data to CSV for analysis
    FILE *delay_file = fopen("outputs/call_center/delay_distribution.csv", "w");
    if (delay_file != NULL) {
        fprintf(delay_file, "actual_delay,predicted_delay,absolute_error,relative_error\n");
        for (int i = 0; i < stats.general_p_stats.delays.size; i++) {
            double actual = stats.general_p_stats.delays.data[i].actual;
            double predicted = stats.general_p_stats.delays.data[i].predicted;
            double abs_error = fabs(predicted - actual);
            double rel_error = fabs(predicted - actual) / fabs(actual);
            fprintf(delay_file, "%.6f,%.6f,%.6f,%.6f\n", actual, predicted, abs_error, rel_error);
        }
        fclose(delay_file);
        printf("\nDelay data saved to outputs/call_center/delay_distribution.csv\n");
    }
    
    // Free memory
    free_delay_array(&stats.general_p_stats.delays);
}

void run_sensitivity_analysis(int gen_opr, int spec_opr, int queue_len) {
    printf("Running sensitivity analysis...\n");
    printf("Configuration: gen=%d, spec=%d, queue=%d\n", gen_opr, spec_opr, queue_len);
    printf("Arrival rate range: %.0f to %.0f calls/hour (step: %.0f)\n", 
           MIN_ARRIVAL_RATE, MAX_ARRIVAL_RATE, ARRIVAL_RATE_STEP);
    printf("Replications per point: %d\n\n", NUM_REPLICATIONS);
    
    FILE *sensitivity_file = fopen("outputs/call_center/sensitivity_analysis.csv", "w");
    if (sensitivity_file == NULL) {
        fprintf(stderr, "Error: Could not open sensitivity analysis output file\n");
        return;
    }
    
    fprintf(sensitivity_file, "arrival_rate,replication,prob_delayed,prob_lost,avg_delay,total_delay\n");
    
    call_center_config config;
    generic_call_gen_only_config gen_call_only;
    generic_call_specific_config gen_call_specific_config;
    general_purpose_config general_p_cfg;
    area_specific_config area_spec_config;
    
    initialize_config(&config, &gen_call_only, &gen_call_specific_config, 
                     &general_p_cfg, &area_spec_config);
    
    config.number_of_gen_opr = gen_opr;
    config.number_of_spec_opr = spec_opr;
    config.length_gen_queue = queue_len;
    
    int total_runs = 0;
    
    int rate_count = 0;
    int total_rates = (int)((MAX_ARRIVAL_RATE - MIN_ARRIVAL_RATE) / ARRIVAL_RATE_STEP) + 1;
    
    for (double arrival_rate = MIN_ARRIVAL_RATE; arrival_rate <= MAX_ARRIVAL_RATE; arrival_rate += ARRIVAL_RATE_STEP) {
        config.arrival_rate = arrival_rate / 3600.0;  // Convert to calls/second
        rate_count++;
        
        for (int rep = 0; rep < NUM_REPLICATIONS; rep++) {
            // Use different seed for each replication
            srand(RANDOM_SEED + total_runs);
            
            call_center_stats stats = start_call_center(config, NUMBER_OF_EVENTS);
            
            fprintf(sensitivity_file, "%.2f,%d,%.6f,%.6f,%.6f,%.6f\n",
                    arrival_rate,
                    rep,
                    stats.general_p_stats.prob_call_delayed,
                    stats.general_p_stats.prob_call_lost,
                    stats.general_p_stats.avg_delay_of_calls,
                    stats.area_spec_stats.avg_answ_time);
            
            free_delay_array(&stats.general_p_stats.delays);
            total_runs++;
            
            // Update progress on same line
            printf("\rTesting arrival rate: %.0f calls/hour [%d/%d] (%.1f%% complete)    ", 
                   arrival_rate, rate_count, total_rates, 100.0 * total_runs / (total_rates * NUM_REPLICATIONS));
            fflush(stdout);
        }
    }
    printf("\n");  // New line after progress completes
    
    fclose(sensitivity_file);
    printf("\nSensitivity analysis complete!\n");
    printf("Results saved to outputs/call_center/sensitivity_analysis.csv\n");
    printf("Total simulations run: %d\n", total_runs);
}

void print_usage(const char *program_name) {
    printf("Usage:\n");
    printf("  %s optimize                    - Run optimization to find best configuration\n", program_name);
    printf("  %s <gen> <spec> <queue>       - Run simulation with specific configuration\n", program_name);
    printf("  %s sensitivity <gen> <spec> <queue> - Run sensitivity analysis\n", program_name);
    printf("\nExamples:\n");
    printf("  %s optimize\n", program_name);
    printf("  %s 2 3 4\n", program_name);
    printf("  %s sensitivity 2 2 2\n", program_name);
}

int main(int argc, char *argv[]) {
    if (argc == 2 && strcmp(argv[1], "optimize") == 0) {
        run_optimization();
    } else if (argc == 4) {
        int gen_opr = atoi(argv[1]);
        int spec_opr = atoi(argv[2]);
        int queue_len = atoi(argv[3]);
        
        if (gen_opr <= 0 || spec_opr <= 0 || queue_len <= 0) {
            fprintf(stderr, "Error: All parameters must be positive integers\n");
            print_usage(argv[0]);
            return 1;
        }
        
        run_simulation(gen_opr, spec_opr, queue_len);
    } else if (argc == 5 && strcmp(argv[1], "sensitivity") == 0) {
        int gen_opr = atoi(argv[2]);
        int spec_opr = atoi(argv[3]);
        int queue_len = atoi(argv[4]);
        
        if (gen_opr <= 0 || spec_opr <= 0 || queue_len <= 0) {
            fprintf(stderr, "Error: All parameters must be positive integers\n");
            print_usage(argv[0]);
            return 1;
        }
        
        run_sensitivity_analysis(gen_opr, spec_opr, queue_len);
    } else {
        fprintf(stderr, "Error: Invalid arguments\n\n");
        print_usage(argv[0]);
        return 1;
    }
    
    return 0;
}