#ifndef SYSTEM_H
#define SYSTEM_H

float erlang_b_system(int channels, int lambda, float avg_duration, int n_samples);
ErlangCstat erlang_c_system(int channels, int lambda, float avg_duration, int n_samples, float delay_threshold);

#endif // SYSTEM_H