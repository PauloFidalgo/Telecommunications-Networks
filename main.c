/**
 * @file main.c
 * @author Paulo Fidalgo
 * @author Wagner Pedrosa
 * @brief Entrypoint of the code
 * @version 0.1
 * @date 2025-09-22
 *
 * @copyright Copyright (c) 2025
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include "event/event-simulations.h"
#include "system/system.h"

void write_result_to_file(Result res, char filename[], int lambda, int n_samples)
{
    FILE *fptr;
    fptr = fopen(filename, "w");

    if (fptr == NULL)
    {
        printf("Error opening file %s\n", filename);
        return;
    }

    fprintf(fptr, "Estimated Average: %f\n", res.average);
    fprintf(fptr, "Theoretical Average: %f\n", res.theoretical_average);
    fprintf(fptr, "Lambda: %d\n", lambda);
    fprintf(fptr, "Number of Samples: %d\n", n_samples);

    fprintf(fptr, "Histogram: ");
    for (int i = 0; i < res.histogram_size; i++)
    {
        fprintf(fptr, "%d", res.histogram[i]);
        if (i < res.histogram_size - 1)
        {
            fprintf(fptr, ",");
        }
    }
    fprintf(fptr, "\n");

    fclose(fptr);
}

void write_erlang_c_to_file(ErlangCstat res, char filename[])
{
    FILE *fptr;
    fptr = fopen(filename, "w");

    if (fptr == NULL)
    {
        printf("Error opening file %s\n", filename);
        return;
    }

    fprintf(fptr, "Estimated Probability of Delayed: %f\n", res.prob_pkt_delayed);
    fprintf(fptr, "Estimated Probability of Delayed more than: %f\n", res.prob_pkt_delayed_more_ax);
    fprintf(fptr, "Average Delay: %f\n", res.avg_delay_all_pkt);

    fprintf(fptr, "Histogram: ");
    for (int i = 0; i < res.histogram_size; i++)
    {
        fprintf(fptr, "%d", res.histogram[i]);
        if (i < res.histogram_size - 1)
        {
            fprintf(fptr, ",");
        }
    }
    fprintf(fptr, "\n");

    fclose(fptr);
}

int main() {
    int lambda = 200;
    int number_events = 100000;
    float avg_time = 0.008;

    int channels[] = {1, 2, 3, 4, 5};
    int num_channels = sizeof(channels) / sizeof(int);

    float thresholds[] = {0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0};
    int num_thresholds = sizeof(channels) / sizeof(float);

    // Test Erlang B system
    for (int i = 0; i < num_channels; i++) {
        float blk = erlang_b_system(channels[i], lambda, avg_time, number_events);
        printf("{%d: %f} - ", i + 1, blk);
    }

    // Test Erlang C system
    for (int i = 0; i < num_channels; i++) {
        for (int j = 0; j < num_thresholds; j++) {
            ErlangCstat erlang_c_res = erlang_c_system(channels[i], lambda, avg_time, number_events, thresholds[j]);

            char filename_event[100];
            sprintf(filename_event, "outputs/erlang_c/num_channels_%d_threshold_%.3f.txt", channels[i], thresholds[j]);
            write_erlang_c_to_file(erlang_c_res, filename_event);
        }
    }

    // Check that Erlang Generic with queue = 0 is the same as Erlang B
    // Run 1 at a Time to get same random values
    for (int i = 0; i < num_channels; i++) {
            ErlangGenStat same_blk = erlang_gen_system(channels[i], lambda, avg_time, number_events, 0.01, 0);
            float blk = erlang_b_system(channels[i], lambda, avg_time, number_events);
            printf("{%d: %f}\n", channels[i], same_blk.block_probability);
            printf("{%d: %f}\n", channels[i], blk);
    }

    // Check that Erlang Generic with queue = infinite is the the same as Erlang C
    // Run 1 at a Time to get same random values
    ErlangGenStat same_infinite = erlang_gen_system(3, lambda, avg_time, number_events, 0.01, 100000);
    ErlangCstat same_infinite_erl = erlang_c_system(3, lambda, avg_time, number_events, 0.01);

    printf("Estimated Probability of Delayed: {%f, %f}\n", same_infinite.prob_pkt_delayed, same_infinite_erl.prob_pkt_delayed);
    printf("Estimated Probability of Delayed more than: {%f, %f}\n", same_infinite.prob_pkt_delayed_more_ax, same_infinite_erl.prob_pkt_delayed_more_ax);
    printf("Average Delay: {%f, %f}\n", same_infinite.avg_delay_all_pkt, same_infinite_erl.avg_delay_all_pkt);

    // Run Erlang Generic for different capacities
    for (int capacity = 0; capacity <= 25; capacity += 5) {
        ErlangGenStat same_infinite = erlang_gen_system(1, lambda, avg_time, number_events, 1.0, capacity);

        printf("-------------------------------\n");
        printf("Result for capacity = %d\n", capacity);
        printf("Estimated Probability of Delayed: %f\n", same_infinite.prob_pkt_delayed);
        printf("Estimated Probability of Delayed more than: %f\n", same_infinite.prob_pkt_delayed_more_ax);
        printf("Average Delay: %f\n", same_infinite.avg_delay_all_pkt);
        printf("Estimated Block Probability: %f\n", same_infinite.block_probability);
        printf("-------------------------------\n");
    }

    // Detect the Length of the Queue for each Channel Capacity in order to get 1% Blocking Probability
    for (int i = 0; i < num_channels; i++) {
        int queue_size = 0;
        ErlangGenStat res = erlang_gen_system(channels[i], lambda, avg_time, number_events, 1.0, queue_size);
        while (res.block_probability > 0.01)
        {
            queue_size += 1;
            res = erlang_gen_system(channels[i], lambda, avg_time, number_events, 1.0, queue_size);
        }

        printf("Channel: %d, Queue Size: %d, Blk Prob: %f\n", channels[i], queue_size, res.block_probability);
    }

    return 0;
}

// Old Main with the tests conducted in Part 1
/*
int main(int argc, char *argv[])
{

    int lambdas[] = {2, 5, 10, 20};
    int num_lambdas = sizeof(lambdas) / sizeof(lambdas[0]);

    int sample_sizes[] = {500, 2000, 5000};
    int num_samples = sizeof(sample_sizes) / sizeof(sample_sizes[0]);

    for (int i = 0; i < num_lambdas; i++)
    {
        int lambda = lambdas[i];

        for (int j = 0; j < num_samples; j++)
        {
            int n_samples = sample_sizes[j];

            Result event_driven = poison_event_driven_simulation(lambda, n_samples);

            Result p_process = poison_process(lambda, n_samples);

            char filename_event[100];
            sprintf(filename_event, "outputs/poison_event_lambda%d_samples%d.txt", lambda, n_samples);
            write_result_to_file(event_driven, filename_event, lambda, n_samples);

            char filename_process[100];
            sprintf(filename_process, "outputs/poison_process_lambda%d_samples%d.txt", lambda, n_samples);
            write_result_to_file(p_process, filename_process, lambda, n_samples);

            free(event_driven.histogram);
            free(p_process.histogram);
        }
    }

    return 0;
}
*/