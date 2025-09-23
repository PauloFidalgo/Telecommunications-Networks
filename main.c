/**
 * @file main.c
 * @author Paulo Fidalgo
 * @author Wagner Pedrosa
 * @brief
 * @version 0.1
 * @date 2025-09-22
 *
 * @copyright Copyright (c) 2025
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include "event/event-simulations.h"

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

            // Run Event-Driven Simulation
            Result event_driven = poison_event_driven_simulation(lambda, n_samples);

            // Run Poisson Process Simulation
            Result p_process = poison_process(lambda, n_samples);

            // Write event-driven results to file
            char filename_event[100];
            sprintf(filename_event, "outputs/poison_event_lambda%d_samples%d.txt", lambda, n_samples);
            write_result_to_file(event_driven, filename_event, lambda, n_samples);

            // Write process results to file
            char filename_process[100];
            sprintf(filename_process, "outputs/poison_process_lambda%d_samples%d.txt", lambda, n_samples);
            write_result_to_file(p_process, filename_process, lambda, n_samples);

            // Free allocated memory
            free(event_driven.histogram);
            free(p_process.histogram);
        }
        printf("\n");
    }

    return 0;
}