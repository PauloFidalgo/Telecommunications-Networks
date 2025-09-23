/**
 * @file poison.c
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
#include <math.h>
#include <time.h>

double next_poison(int lambda)
{
    double u;
    do
    {
        u = (double)rand() / (double)RAND_MAX;
    } while (u == 0.0 || u == 1.0);

    return -(1.0 / lambda) * log(u);
}
