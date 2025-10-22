/**
 * @file models.h
 * @author Paulo Fidalgo
 * @author Wagner Pedrosa
 * @brief Header file defining data structures and constants for simulation models
 * @version 0.1
 * @date 2025-09-22
 *
 * @copyright Copyright (c) 2025
 *
 */

typedef struct
{
    double average;
    double theoretical_average;
    int *histogram;
    int histogram_size;
} Result;

typedef struct 
{
    double prob_pkt_delayed;
    double avg_delay_all_pkt;
    int *histogram;
    int histogram_size;
    double prob_pkt_delayed_more_ax;
} ErlangCstat;

typedef struct 
{
    double prob_pkt_delayed;
    double avg_delay_all_pkt;
    int *histogram;
    int histogram_size;
    double prob_pkt_delayed_more_ax;
    double block_probability;
} ErlangGenStat;