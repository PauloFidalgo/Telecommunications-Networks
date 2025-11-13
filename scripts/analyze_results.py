#!/usr/bin/env python3
"""
Analyze and visualize simulation results for the call center system.
This script generates plots for:
1. Distribution of delays
2. Histogram of prediction errors
3. Sensitivity analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "outputs" / "call_center"
PLOTS_DIR = BASE_DIR / "plots" / "call_center"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def plot_delay_distribution(delay_file):
    """Plot the distribution of actual delays."""
    df = pd.read_csv(delay_file)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram
    axes[0].hist(df['actual_delay'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    axes[0].set_xlabel('Delay (seconds)')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Distribution of Call Delays\n(General-Purpose Queue)')
    axes[0].axvline(df['actual_delay'].mean(), color='red', linestyle='--', 
                    label=f'Mean: {df["actual_delay"].mean():.2f}s')
    axes[0].axvline(df['actual_delay'].median(), color='green', linestyle='--', 
                    label=f'Median: {df["actual_delay"].median():.2f}s')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # CDF
    sorted_delays = np.sort(df['actual_delay'])
    cdf = np.arange(1, len(sorted_delays) + 1) / len(sorted_delays)
    axes[1].plot(sorted_delays, cdf, linewidth=2, color='steelblue')
    axes[1].set_xlabel('Delay (seconds)')
    axes[1].set_ylabel('Cumulative Probability')
    axes[1].set_title('Cumulative Distribution Function (CDF) of Delays')
    axes[1].grid(True, alpha=0.3)
    
    # Add percentile markers
    percentiles = [50, 75, 90, 95]
    for p in percentiles:
        val = np.percentile(df['actual_delay'], p)
        axes[1].axhline(p/100, color='gray', linestyle=':', alpha=0.5)
        axes[1].axvline(val, color='gray', linestyle=':', alpha=0.5)
        axes[1].text(val, p/100 + 0.02, f'{p}th: {val:.1f}s', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'delay_distribution.png', dpi=300, bbox_inches='tight')
    plt.savefig(PLOTS_DIR / 'delay_distribution.pdf', bbox_inches='tight')
    print(f"✓ Delay distribution plot saved to {PLOTS_DIR / 'delay_distribution.png'}")
    
    # Print statistics
    print("\n" + "="*60)
    print("DELAY STATISTICS")
    print("="*60)
    print(f"Number of delayed calls: {len(df)}")
    print(f"Mean delay: {df['actual_delay'].mean():.2f} s")
    print(f"Median delay: {df['actual_delay'].median():.2f} s")
    print(f"Std deviation: {df['actual_delay'].std():.2f} s")
    print(f"Min delay: {df['actual_delay'].min():.2f} s")
    print(f"Max delay: {df['actual_delay'].max():.2f} s")
    print(f"\nPercentiles:")
    for p in [25, 50, 75, 90, 95, 99]:
        print(f"  {p}th percentile: {np.percentile(df['actual_delay'], p):.2f} s")


def plot_prediction_errors(delay_file):
    """Plot histograms of prediction errors."""
    df = pd.read_csv(delay_file)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Absolute error histogram
    axes[0, 0].hist(df['absolute_error'], bins=30, edgecolor='black', alpha=0.7, color='coral')
    axes[0, 0].set_xlabel('Absolute Prediction Error (seconds)')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Distribution of Absolute Prediction Errors')
    axes[0, 0].axvline(df['absolute_error'].mean(), color='red', linestyle='--', 
                       label=f'Mean: {df["absolute_error"].mean():.2f}s')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Relative error histogram
    axes[0, 1].hist(df['relative_error'], bins=30, edgecolor='black', alpha=0.7, color='lightgreen')
    axes[0, 1].set_xlabel('Relative Prediction Error')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Distribution of Relative Prediction Errors')
    axes[0, 1].axvline(df['relative_error'].mean(), color='red', linestyle='--', 
                       label=f'Mean: {df["relative_error"].mean():.4f}')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Predicted vs Actual scatter plot
    axes[1, 0].scatter(df['actual_delay'], df['predicted_delay'], alpha=0.5, s=20)
    max_val = max(df['actual_delay'].max(), df['predicted_delay'].max())
    axes[1, 0].plot([0, max_val], [0, max_val], 'r--', label='Perfect prediction')
    axes[1, 0].set_xlabel('Actual Delay (seconds)')
    axes[1, 0].set_ylabel('Predicted Delay (seconds)')
    axes[1, 0].set_title('Predicted vs Actual Delay')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Error over time (sequence)
    axes[1, 1].plot(df['absolute_error'], alpha=0.6, linewidth=0.8)
    axes[1, 1].axhline(df['absolute_error'].mean(), color='red', linestyle='--', 
                       label=f'Mean: {df["absolute_error"].mean():.2f}s')
    axes[1, 1].set_xlabel('Call Index')
    axes[1, 1].set_ylabel('Absolute Error (seconds)')
    axes[1, 1].set_title('Prediction Error Over Time')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'prediction_errors.png', dpi=300, bbox_inches='tight')
    plt.savefig(PLOTS_DIR / 'prediction_errors.pdf', bbox_inches='tight')
    print(f"✓ Prediction error plots saved to {PLOTS_DIR / 'prediction_errors.png'}")
    
    # Print statistics
    print("\n" + "="*60)
    print("PREDICTION ERROR STATISTICS")
    print("="*60)
    print(f"Mean absolute error: {df['absolute_error'].mean():.2f} s")
    print(f"Std absolute error: {df['absolute_error'].std():.2f} s")
    print(f"Mean relative error: {df['relative_error'].mean():.4f}")
    print(f"Std relative error: {df['relative_error'].std():.4f}")
    
    # Calculate correlation
    correlation = np.corrcoef(df['actual_delay'], df['predicted_delay'])[0, 1]
    print(f"\nCorrelation (predicted vs actual): {correlation:.4f}")


def plot_sensitivity_analysis(sensitivity_file, nominal_rate=80.0):
    """Plot sensitivity analysis results with confidence intervals."""
    df = pd.read_csv(sensitivity_file)
    
    # Group by arrival rate and calculate statistics
    grouped = df.groupby('arrival_rate').agg({
        'total_delay': ['mean', 'std', 'count'],
        'prob_delayed': ['mean', 'std'],
        'prob_lost': ['mean', 'std'],
        'avg_delay': ['mean', 'std']
    })
    
    # Calculate 90% confidence intervals
    confidence = 0.90
    alpha = 1 - confidence
    
    arrival_rates = grouped.index.values
    total_delay_mean = grouped['total_delay']['mean'].values
    total_delay_std = grouped['total_delay']['std'].values
    n = grouped['total_delay']['count'].values
    
    # t-value for 90% CI
    t_values = [stats.t.ppf(1 - alpha/2, n_i - 1) for n_i in n]
    total_delay_ci = [t * std / np.sqrt(n_i) for t, std, n_i in zip(t_values, total_delay_std, n)]
    
    # Create plots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Main plot: Total delay vs arrival rate with CI
    axes[0, 0].plot(arrival_rates, total_delay_mean, 'o-', linewidth=2, markersize=6, 
                    color='steelblue', label='Mean total delay')
    axes[0, 0].fill_between(arrival_rates, 
                             total_delay_mean - total_delay_ci, 
                             total_delay_mean + total_delay_ci,
                             alpha=0.3, color='steelblue', label='90% CI')
    axes[0, 0].axvline(nominal_rate, color='red', linestyle='--', alpha=0.7, 
                       label=f'Nominal rate ({nominal_rate} calls/h)')
    axes[0, 0].set_xlabel('Arrival Rate (calls/hour)')
    axes[0, 0].set_ylabel('Average Total Delay (seconds)')
    axes[0, 0].set_title('Sensitivity Analysis: Total Delay vs Arrival Rate')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Zoom around nominal rate
    nominal_idx = np.argmin(np.abs(arrival_rates - nominal_rate))
    zoom_range = 3  # Show ±3 points around nominal
    start_idx = max(0, nominal_idx - zoom_range)
    end_idx = min(len(arrival_rates), nominal_idx + zoom_range + 1)
    
    axes[0, 1].plot(arrival_rates[start_idx:end_idx], 
                    total_delay_mean[start_idx:end_idx], 
                    'o-', linewidth=2, markersize=8, color='steelblue')
    axes[0, 1].fill_between(arrival_rates[start_idx:end_idx],
                             total_delay_mean[start_idx:end_idx] - np.array(total_delay_ci)[start_idx:end_idx],
                             total_delay_mean[start_idx:end_idx] + np.array(total_delay_ci)[start_idx:end_idx],
                             alpha=0.3, color='steelblue')
    axes[0, 1].axvline(nominal_rate, color='red', linestyle='--', alpha=0.7)
    axes[0, 1].set_xlabel('Arrival Rate (calls/hour)')
    axes[0, 1].set_ylabel('Average Total Delay (seconds)')
    axes[0, 1].set_title(f'Zoomed View Around Nominal Rate ({nominal_rate} calls/h)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Probability delayed
    prob_delayed_mean = grouped['prob_delayed']['mean'].values
    axes[1, 0].plot(arrival_rates, prob_delayed_mean, 'o-', linewidth=2, 
                    markersize=6, color='orange')
    axes[1, 0].axvline(nominal_rate, color='red', linestyle='--', alpha=0.7)
    axes[1, 0].set_xlabel('Arrival Rate (calls/hour)')
    axes[1, 0].set_ylabel('Probability of Delay')
    axes[1, 0].set_title('Probability of Delay vs Arrival Rate')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Probability lost
    prob_lost_mean = grouped['prob_lost']['mean'].values
    axes[1, 1].plot(arrival_rates, prob_lost_mean, 'o-', linewidth=2, 
                    markersize=6, color='red')
    axes[1, 1].axvline(nominal_rate, color='red', linestyle='--', alpha=0.7)
    axes[1, 1].set_xlabel('Arrival Rate (calls/hour)')
    axes[1, 1].set_ylabel('Probability of Loss')
    axes[1, 1].set_title('Probability of Loss vs Arrival Rate')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'sensitivity_analysis.png', dpi=300, bbox_inches='tight')
    plt.savefig(PLOTS_DIR / 'sensitivity_analysis.pdf', bbox_inches='tight')
    print(f"✓ Sensitivity analysis plot saved to {PLOTS_DIR / 'sensitivity_analysis.png'}")
    
    # Print statistics for nominal rate
    print("\n" + "="*60)
    print(f"CONFIDENCE INTERVAL ANALYSIS (Arrival rate = {nominal_rate} calls/hour)")
    print("="*60)
    nominal_data = df[df['arrival_rate'] == nominal_rate]['total_delay']
    mean_delay = nominal_data.mean()
    std_delay = nominal_data.std()
    n_samples = len(nominal_data)
    t_val = stats.t.ppf(1 - alpha/2, n_samples - 1)
    ci_half_width = t_val * std_delay / np.sqrt(n_samples)
    
    print(f"Number of replications: {n_samples}")
    print(f"Mean total delay: {mean_delay:.2f} s")
    print(f"Standard deviation: {std_delay:.2f} s")
    print(f"90% Confidence Interval: [{mean_delay - ci_half_width:.2f}, {mean_delay + ci_half_width:.2f}] s")
    print(f"CI half-width: ±{ci_half_width:.2f} s")
    print(f"Relative half-width: {(ci_half_width / mean_delay * 100):.2f}%")
    
    return grouped


def generate_summary_report(delay_file, sensitivity_file):
    """Generate a comprehensive text report."""
    delay_df = pd.read_csv(delay_file)
    sens_df = pd.read_csv(sensitivity_file)
    
    report_file = PLOTS_DIR / 'simulation_report.txt'
    
    with open(report_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write("CALL CENTER SIMULATION - COMPREHENSIVE REPORT\n")
        f.write("="*70 + "\n\n")
        
        f.write("1. DELAY DISTRIBUTION STATISTICS\n")
        f.write("-" * 70 + "\n")
        f.write(f"   Number of delayed calls: {len(delay_df)}\n")
        f.write(f"   Mean delay: {delay_df['actual_delay'].mean():.2f} s\n")
        f.write(f"   Median delay: {delay_df['actual_delay'].median():.2f} s\n")
        f.write(f"   Std deviation: {delay_df['actual_delay'].std():.2f} s\n")
        f.write(f"   Min delay: {delay_df['actual_delay'].min():.2f} s\n")
        f.write(f"   Max delay: {delay_df['actual_delay'].max():.2f} s\n")
        f.write(f"\n   Percentiles:\n")
        for p in [25, 50, 75, 90, 95, 99]:
            f.write(f"     {p}th: {np.percentile(delay_df['actual_delay'], p):.2f} s\n")
        
        f.write("\n2. PREDICTION ERROR STATISTICS\n")
        f.write("-" * 70 + "\n")
        f.write(f"   Mean absolute error: {delay_df['absolute_error'].mean():.2f} s\n")
        f.write(f"   Std absolute error: {delay_df['absolute_error'].std():.2f} s\n")
        f.write(f"   Mean relative error: {delay_df['relative_error'].mean():.4f}\n")
        f.write(f"   Std relative error: {delay_df['relative_error'].std():.4f}\n")
        corr = np.corrcoef(delay_df['actual_delay'], delay_df['predicted_delay'])[0, 1]
        f.write(f"   Correlation (predicted vs actual): {corr:.4f}\n")
        
        f.write("\n3. SENSITIVITY ANALYSIS (Nominal rate = 80 calls/hour)\n")
        f.write("-" * 70 + "\n")
        nominal_data = sens_df[sens_df['arrival_rate'] == 80.0]['total_delay']
        mean_delay = nominal_data.mean()
        std_delay = nominal_data.std()
        n_samples = len(nominal_data)
        t_val = stats.t.ppf(0.95, n_samples - 1)
        ci_half_width = t_val * std_delay / np.sqrt(n_samples)
        
        f.write(f"   Number of replications: {n_samples}\n")
        f.write(f"   Mean total delay: {mean_delay:.2f} s\n")
        f.write(f"   Standard deviation: {std_delay:.2f} s\n")
        f.write(f"   90% CI: [{mean_delay - ci_half_width:.2f}, {mean_delay + ci_half_width:.2f}] s\n")
        f.write(f"   CI half-width: ±{ci_half_width:.2f} s\n")
        f.write(f"   Relative half-width: {(ci_half_width / mean_delay * 100):.2f}%\n")
        
        f.write("\n" + "="*70 + "\n")
    
    print(f"✓ Summary report saved to {report_file}")


def main():
    """Main function to generate all plots and reports."""
    print("\n" + "="*70)
    print("CALL CENTER SIMULATION - RESULTS ANALYSIS")
    print("="*70 + "\n")
    
    delay_file = DATA_DIR / "delay_distribution.csv"
    sensitivity_file = DATA_DIR / "sensitivity_analysis.csv"
    
    # Check if files exist
    if not delay_file.exists():
        print(f"Error: {delay_file} not found!")
        print("Please run: ./main 2 2 2 (or your optimal configuration)")
        return
    
    # Generate plots
    print("Generating plots...\n")
    plot_delay_distribution(delay_file)
    plot_prediction_errors(delay_file)
    
    if sensitivity_file.exists():
        plot_sensitivity_analysis(sensitivity_file)
        generate_summary_report(delay_file, sensitivity_file)
    else:
        print(f"\nNote: {sensitivity_file} not found.")
        print("Run sensitivity analysis with: ./main sensitivity 2 2 2")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE!")
    print("="*70)
    print(f"All plots saved to: {PLOTS_DIR}")
    print("\nGenerated files:")
    for f in PLOTS_DIR.glob('*'):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
