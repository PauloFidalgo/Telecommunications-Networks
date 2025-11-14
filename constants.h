#ifndef CONSTANTS_H
#define CONSTANTS_H

// System inherent parameters
#define ARRIVAL_RATE_PER_HOUR 80.0
#define ARRIVAL_RATE (ARRIVAL_RATE_PER_HOUR / 3600.0)  // Convert to calls per second
#define GENERAL_PURPOSE_RATIO 0.3

// General-purpose call configuration (generic-only calls)
#define GEN_CALL_MIN_DURATION_S 60.0
#define GEN_CALL_AVG_DURATION_S 120.0
#define GEN_CALL_MAX_DURATION_S 300.0

// General-purpose call configuration (area-specific calls served by general operators)
#define SPEC_MIN_DURATION_S 30.0
#define SPEC_AVG_DURATION_S 60.0
#define SPEC_STD_DURATION_S 20.0
#define SPEC_MAX_DURATION_S 120.0

// Area-specific call configuration
#define AREA_SPEC_MIN_DURATION_S 60.0
#define AREA_SPEC_AVG_DURATION_S 150.0

// Simulation parameters
#define NUMBER_OF_EVENTS 100000
#define RANDOM_SEED 42  // Fixed seed for reproducibility (use 0 for time-based random seed)

// Sensitivity analysis parameters
#define NUM_REPLICATIONS 30  // Number of independent replications for confidence interval
#define MIN_ARRIVAL_RATE 50.0  // Minimum arrival rate for sensitivity analysis (calls/hour)
#define MAX_ARRIVAL_RATE 120.0  // Maximum arrival rate for sensitivity analysis (calls/hour)
#define ARRIVAL_RATE_STEP 5.0  // Step size for arrival rate variation (calls/hour)

#endif // CONSTANTS_H
