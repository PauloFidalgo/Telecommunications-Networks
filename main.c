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
//#include "system/system.h"
#include "call_center/call_center.h"


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
    call_center_config config;
    config.number_of_gen_opr = 2;
    config.number_of_spec_opr = 2;
    config.length_gen_queue = 2;
    config.arrival_rate = 80;
    config.general_purpose_ratio = 0.3;


    start_call_center(config, 10000);
}