#ifndef SYSTEM_H
#define SYSTEM_H

double erlang_b_system(int channels, int lambda, double avg_duration, int n_samples);
ErlangCstat erlang_c_system(int channels, int lambda, double avg_duration, int n_samples, double delay_threshold);
ErlangGenStat erlang_gen_system(int channels, int lambda, double avg_duration, int n_samples, double delay_threshold, int queue_capacity);

#endif // SYSTEM_H