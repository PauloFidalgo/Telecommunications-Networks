#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "call_center/call_center.h"

int main() {
    printf("Starting MSE-based optimization...\n");
    printf("Searching 1-100 for each parameter (1,000,000 configs)\n\n");
    
    // Target values
    double target_delayed = 0.30;  
    double target_lost = 0.02;    
    double target_avg_delay = 30.0; 
    double target_total_delay = 90.0; 
    
    call_center_config config;
    config.arrival_rate = 80.0 / 3600.0;
    config.general_purpose_ratio = 0.3;
    
    generic_call_gen_only_config gen_call_only = {60.0, 120.0, 300.0};
    generic_call_specific_config gen_call_specific_config = {30.0, 60.0, 20.0, 120.0};
    
    general_purpose_config general_p_cfg;
    general_p_cfg.gen_call_gen_only_config = &gen_call_only;
    general_p_cfg.gen_call_specific_config = &gen_call_specific_config;
    
    config.general_p_config = &general_p_cfg;
    
    area_specific_config area_spec_config = {60.0, 150.0};
    config.area_spec_config = &area_spec_config;
    
    int number_of_events = 10000;
    
    double best_mse = 1e9;
    int best_gen = 0, best_spec = 0, best_queue = 0;
    call_center_stats best_stats;
    
    int count = 0;
    int total = 100 * 100 * 100;
    
    for (int gen_opr = 1; gen_opr <= 100; gen_opr++) {
        for (int spec_opr = 1; spec_opr <= 100; spec_opr++) {
            for (int queue_len = 1; queue_len <= 100; queue_len++) {
                count++;
                
                config.number_of_gen_opr = gen_opr;
                config.number_of_spec_opr = spec_opr;
                config.length_gen_queue = queue_len;
                
                call_center_stats stats = start_call_center(config, number_of_events);
                
                double mse_delayed = pow(stats.general_p_stats.prob_call_delayed - target_delayed, 2);
                double mse_lost = pow(stats.general_p_stats.prob_call_lost - target_lost, 2);
                double mse_avg_delay = pow(stats.general_p_stats.avg_delay_of_calls - target_avg_delay, 2);
                double mse_total_delay = pow(stats.area_spec_stats.avg_answ_time - target_total_delay, 2);
                
                double total_mse = mse_delayed + mse_lost + mse_avg_delay + mse_total_delay;
                
                if (total_mse < best_mse) {
                    best_mse = total_mse;
                    best_gen = gen_opr;
                    best_spec = spec_opr;
                    best_queue = queue_len;
                    best_stats = stats;
                    
                    printf("[%d/%d] NEW BEST: gen=%d, spec=%d, queue=%d | MSE=%.6f\n",
                           count, total, gen_opr, spec_opr, queue_len, total_mse);
                    printf("  Delayed: %.4f (target: %.2f)\n", stats.general_p_stats.prob_call_delayed, target_delayed);
                    printf("  Lost: %.4f (target: %.2f)\n", stats.general_p_stats.prob_call_lost, target_lost);
                    printf("  Avg delay: %.2f (target: %.2f)\n", stats.general_p_stats.avg_delay_of_calls, target_avg_delay);
                    printf("  Total delay: %.2f (target: %.2f)\n\n", stats.area_spec_stats.avg_answ_time, target_total_delay);
                }
                
                if (count % 10000 == 0) {
                    printf("Progress: %d/%d (%.1f%%)\n", count, total, 100.0 * count / total);
                }
            }
        }
    }
    
    printf("\n========================================\n");
    printf("OPTIMIZATION COMPLETE\n");
    printf("========================================\n\n");
    printf("Best configuration found:\n");
    printf("  General operators: %d\n", best_gen);
    printf("  Specialist operators: %d\n", best_spec);
    printf("  Queue length: %d\n", best_queue);
    printf("  Total MSE: %.6f\n\n", best_mse);
    
    printf("Performance:\n");
    printf("  Prob. delayed: %.4f (target: %.2f)\n", best_stats.general_p_stats.prob_call_delayed, target_delayed);
    printf("  Prob. lost: %.4f (target: %.2f)\n", best_stats.general_p_stats.prob_call_lost, target_lost);
    printf("  Avg delay: %.2f s (target: %.2f s)\n", best_stats.general_p_stats.avg_delay_of_calls, target_avg_delay);
    printf("  Total delay: %.2f s (target: %.2f s)\n", best_stats.area_spec_stats.avg_answ_time, target_total_delay);
    
    return 0;
}