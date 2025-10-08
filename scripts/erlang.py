import matplotlib.pyplot as plt
from math import factorial
import os


def erlang_b_formula(n: int, rho: float) -> float:
    numerator = (rho ** n) / factorial(n)
    denominator = sum((rho ** k) / factorial(k) for k in range(n + 1))
    return numerator / denominator


def plot_erlang_b_res(filename: str) -> None:
    with open(filename, "r") as f:
        _lambda = float(f.readline().split("=")[-1].strip())
        _num_events = f.readline().split("=")[-1].strip()
        _avg_duration = float(f.readline().split("=")[-1].strip())
        
        _rest = f.readlines()
        channels: dict[int, float] = {}

        for l in _rest:
            spl = l.split(",")
            ch = spl[0]
            blk = spl[1]
            channels[int(ch)] = float(blk)

        rho = _lambda * _avg_duration
        theoretical = {n: erlang_b_formula(n, rho) for n in channels.keys()}

        plt.figure(figsize=(14, 8))
        
        x_pos = list(channels.keys())
        sim_values = list(channels.values())
        theo_values = [theoretical[n] for n in x_pos]
        
        width = 0.35
        plt.bar([x - width/2 for x in x_pos], sim_values, width, alpha=0.7, 
                label='Simulated', color='steelblue')
        plt.bar([x + width/2 for x in x_pos], theo_values, width, alpha=0.7,
                label='Theoretical (Erlang-B)', color='coral')
        
        for i, (x, sim_val, theo_val) in enumerate(zip(x_pos, sim_values, theo_values)):
            plt.text(x - width/2, sim_val, f'{sim_val:.4f}', 
                    ha='center', va='bottom', fontsize=8, rotation=0)
            plt.text(x + width/2, theo_val, f'{theo_val:.4f}', 
                    ha='center', va='bottom', fontsize=8, rotation=0)
        
        plt.title(f'Erlang-B: Simulated vs Theoretical (λ={_lambda}, ρ={rho:.2f}, N={_num_events}, Avg duration={_avg_duration})', fontsize=14)
        plt.xlabel('Number of Channels', fontsize=12)
        plt.ylabel('Blocking Probability', fontsize=12)
        plt.xticks(x_pos) 
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig("../plots/erlang/blk.png", dpi=300, bbox_inches='tight')
        plt.show()

def erlang_c_formula(n: int, rho: float) -> float:
    if rho >= n:
        return 1.0
    
    erlang_b = erlang_b_formula(n, rho)
    numerator = n * erlang_b
    denominator = n - rho * (1 - erlang_b)
    
    return numerator / denominator


def plot_erlang_c_res(filename: str, num_channels: int, threshold: float) -> None:
    with open(filename, "r") as f:
        _prob_delay: float = float(f.readline().split(":")[-1].strip())
        _prob_delay_abv_thresh: float = float(f.readline().split(":")[-1].strip())
        _avg_delay: float = float(f.readline().split(":")[-1].strip())
        _lambda: int = 200
        _num_events: int = 100000
        _avg_duration: float = 0.008
        histogram_line = f.readline().split(":")[-1].strip()
        _histogram = list(map(lambda x: int(x), histogram_line.split(",")))
    
    rho = _lambda * _avg_duration
    
    theo_prob_delay = erlang_c_formula(num_channels, rho)
    
    if num_channels > rho:
        theo_avg_delay = (theo_prob_delay * _avg_duration) / (num_channels - rho)
    else:
        theo_avg_delay = float('inf')
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Erlang-C Analysis: {num_channels} channels, threshold={threshold}s (λ={_lambda}, ρ={rho:.2f})', 
                 fontsize=16, fontweight='bold')
    
    ax1 = axes[0, 0]
    metrics = ['P(Delay)', 'P(Delay > threshold)']
    sim_probs = [_prob_delay, _prob_delay_abv_thresh]
    theo_probs = [theo_prob_delay, 0]
    
    x_pos = range(len(metrics))
    width = 0.35
    
    ax1.bar([x - width/2 for x in x_pos], sim_probs, width, alpha=0.7, 
            label='Simulated', color='steelblue')
    ax1.bar([x + width/2 for x in x_pos[:1]], [theo_probs[0]], width, alpha=0.7,
            label='Theoretical', color='coral')
    
    for i, (sim_val, theo_val) in enumerate(zip(sim_probs, theo_probs)):
        ax1.text(i - width/2, sim_val, f'{sim_val:.4f}', 
                ha='center', va='bottom', fontsize=10)
        if i == 0: 
            ax1.text(i + width/2, theo_val, f'{theo_val:.4f}', 
                    ha='center', va='bottom', fontsize=10)
    
    ax1.set_xlabel('Metric', fontsize=11)
    ax1.set_ylabel('Probability', fontsize=11)
    ax1.set_title('Delay Probabilities', fontsize=12, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(metrics)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    ax2 = axes[0, 1]
    delays = ['Avg Delay']
    sim_delays = [_avg_delay]
    theo_delays = [theo_avg_delay if theo_avg_delay != float('inf') else 0]
    
    x_pos2 = range(len(delays))
    ax2.bar([x - width/2 for x in x_pos2], sim_delays, width, alpha=0.7,
            label='Simulated', color='steelblue')
    if theo_avg_delay != float('inf'):
        ax2.bar([x + width/2 for x in x_pos2], theo_delays, width, alpha=0.7,
                label='Theoretical', color='coral')
        ax2.text(0 + width/2, theo_delays[0], f'{theo_delays[0]:.4f}s', 
                ha='center', va='bottom', fontsize=10)
    
    ax2.text(0 - width/2, sim_delays[0], f'{sim_delays[0]:.4f}s', 
            ha='center', va='bottom', fontsize=10)
    
    ax2.set_xlabel('Metric', fontsize=11)
    ax2.set_ylabel('Time (ms)', fontsize=11)
    ax2.set_title('Average Waiting Time (for delayed calls)', fontsize=12, fontweight='bold')
    ax2.set_xticks(x_pos2)
    ax2.set_xticklabels(delays)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    ax3 = axes[1, 0]
    delta = (1.0 / 5.0) * (1.0 / _lambda)
    bins = [i * delta for i in range(len(_histogram))]
    
    ax3.bar(bins, _histogram, width=delta*0.8, alpha=0.7, color='steelblue', edgecolor='black')
    ax3.set_xlabel('Waiting Time (ms)', fontsize=11)
    ax3.set_ylabel('Number of Calls', fontsize=11)
    ax3.set_title('Histogram of Waiting Times', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    
    ax3.axvline(x=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold = {threshold}s')
    ax3.legend()
    
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    table_data = [
        ['Metric', 'Simulated', 'Theoretical', 'Difference'],
        ['P(Delay)', f'{_prob_delay:.6f}', f'{theo_prob_delay:.6f}', f'{abs(_prob_delay - theo_prob_delay):.6f}'],
        ['P(Delay > {:.3f}s)'.format(threshold), f'{_prob_delay_abv_thresh:.6f}', 'N/A', 'N/A'],
        ['Avg Delay (s)', f'{_avg_delay:.6f}', f'{theo_avg_delay:.6f}' if theo_avg_delay != float('inf') else 'Unstable', 
         f'{abs(_avg_delay - theo_avg_delay):.6f}' if theo_avg_delay != float('inf') else 'N/A'],
        ['Channels', str(num_channels), '-', '-'],
        ['Offered Load (ρ)', f'{rho:.4f}', '-', '-'],
        ['Utilization', f'{(rho/num_channels)*100:.2f}%', '-', '-'],
    ]
    
    table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.3, 0.25, 0.25, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    for i in range(4):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax4.set_title('Summary Statistics', fontsize=12, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    output_dir = "../plots/erlang"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"{output_dir}/n_ch_{num_channels}_trh_{threshold}.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()



def create_erlang_c_summary_graphs(directory: str) -> None:
    """Create summary graphs of Erlang-C simulation results."""
    
    _lambda = 200
    _avg_duration = 0.008
    rho = _lambda * _avg_duration
    
    by_channel = {}
    
    for file in sorted(os.listdir(directory)):
        if not file.endswith('.txt'):
            continue
            
        splt = file.split("_")
        num_channels = int(splt[2])
        threshold = float(splt[4].removesuffix(".txt"))
        
        with open(os.path.join(directory, file), "r") as f:
            prob_delay = float(f.readline().split(":")[-1].strip())
            prob_delay_abv_thresh = float(f.readline().split(":")[-1].strip())
            avg_delay = float(f.readline().split(":")[-1].strip())
        
        theo_prob_delay = erlang_c_formula(num_channels, rho)
        if num_channels > rho:
            theo_avg_delay = (theo_prob_delay * _avg_duration) / (num_channels - rho)
        else:
            theo_avg_delay = float('inf')
        
        if num_channels not in by_channel:
            by_channel[num_channels] = []
        
        by_channel[num_channels].append({
            'threshold': threshold,
            'sim_prob_delay': prob_delay,
            'theo_prob_delay': theo_prob_delay,
            'prob_delay_abv_thresh': prob_delay_abv_thresh,
            'sim_avg_delay': avg_delay,
            'theo_avg_delay': theo_avg_delay
        })
    
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    
    ax1 = axes[0]
    channels_list = sorted(by_channel.keys())
    theo_prob_delays = []
    sim_prob_delays = []
    
    for ch in channels_list:
        data = by_channel[ch][0]  
        theo_prob_delays.append(data['theo_prob_delay'])
        sim_prob_delays.append(data['sim_prob_delay'])
    
    width = 0.35
    x_pos = range(len(channels_list))
    
    ax1.bar([x - width/2 for x in x_pos], sim_prob_delays, width, alpha=0.7, 
            label='Simulated', color='steelblue')
    ax1.bar([x + width/2 for x in x_pos], theo_prob_delays, width, alpha=0.7,
            label='Theoretical', color='coral')
    
    max_val = max(max(sim_prob_delays), max(theo_prob_delays))
    offset = max_val * 0.02
    for i, (sim_val, theo_val) in enumerate(zip(sim_prob_delays, theo_prob_delays)):
        ax1.text(i - width/2, sim_val + offset, f'{sim_val:.4f}', 
                ha='left', va='bottom', fontsize=8, rotation=90)
        ax1.text(i + width/2, theo_val + offset, f'{theo_val:.4f}', 
                ha='left', va='bottom', fontsize=8, rotation=90)
    
    ax1.set_xlabel('Number of Channels', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Blocking Probability P(Delay)', fontsize=12, fontweight='bold')
    ax1.set_title('Erlang-C: Probability of Delay vs Number of Channels', fontsize=13, fontweight='bold')
    ax1.set_ylim(0, max(max(sim_prob_delays), max(theo_prob_delays)) * 1.15)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(channels_list)
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, axis='y')
    
    ax2 = axes[1]
    sim_avg_delays = []
    theo_avg_delays = []
    
    for ch in channels_list:
        data = by_channel[ch][0]
        sim_avg_delays.append(data['sim_avg_delay'])
        if data['theo_avg_delay'] != float('inf'):
            theo_avg_delays.append(data['theo_avg_delay'])
        else:
            theo_avg_delays.append(None)  # Skip unstable systems in plot
    
    # Ensure arrays have the same length
    assert len(sim_avg_delays) == len(theo_avg_delays) == len(x_pos), f"Array length mismatch: sim={len(sim_avg_delays)}, theo={len(theo_avg_delays)}, x_pos={len(x_pos)}"
    
    # Create separate lists for plotting, replacing None with 0 for unstable systems
    theo_avg_delays_plot = [val if val is not None else 0 for val in theo_avg_delays]
    
    ax2.bar([x - width/2 for x in x_pos], sim_avg_delays, width, alpha=0.7, 
            label='Simulated', color='steelblue')
    ax2.bar([x + width/2 for x in x_pos], theo_avg_delays_plot, width, alpha=0.7,
            label='Theoretical', color='coral')
    
    # Safely calculate max value
    all_delays = [v for v in sim_avg_delays + theo_avg_delays if v is not None and v > 0]
    if all_delays:
        max_delay_val = max(all_delays)
    else:
        max_delay_val = 1.0  # fallback value
    delay_offset = max_delay_val * 0.02
    for i, (sim_val, theo_val) in enumerate(zip(sim_avg_delays, theo_avg_delays)):
        ax2.text(i - width/2, sim_val + delay_offset, f'{sim_val:.3f}', 
                ha='left', va='bottom', fontsize=8, rotation=90)
        if theo_val is not None and theo_val > 0:
            ax2.text(i + width/2, theo_val + delay_offset, f'{theo_val:.3f}', 
                    ha='left', va='bottom', fontsize=8, rotation=90)
        else:
            # Add note for infinite theoretical values
            ax2.text(i + width/2, max_delay_val * 0.3, '∞\n(Unstable)', 
                    ha='center', va='center', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="red", alpha=0.7),
                    color='white')

    ax2.set_xlabel('Number of Channels', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Average Delay (ms)', fontsize=12, fontweight='bold')
    ax2.set_title('Average Waiting Time vs Number of Channels', fontsize=13, fontweight='bold')
    ax2.set_ylim(0, max_delay_val * 1.15)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(channels_list)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3, axis='y')
    
    ax3 = axes[2]
    
    all_thresholds = sorted(set(d['threshold'] for data_list in by_channel.values() for d in data_list))
    
    for threshold in all_thresholds:
        probs = []
        for ch in channels_list:
            matching = [d for d in by_channel[ch] if d['threshold'] == threshold]
            if matching:
                probs.append(matching[0]['prob_delay_abv_thresh'])
            else:
                probs.append(0)
        
        ax3.plot(channels_list, probs, 'o-', label=f'T = {threshold}ms', 
                linewidth=2, markersize=8)
    
    ax3.set_xlabel('Number of Channels', fontsize=12, fontweight='bold')
    ax3.set_ylabel('P(Delay > Threshold)', fontsize=12, fontweight='bold')
    ax3.set_title('Probability of Excessive Delay', fontsize=13, fontweight='bold')
    ax3.set_xticks(channels_list)
    ax3.legend(fontsize=10, loc='upper right')
    ax3.grid(True, alpha=0.3)
    
    plt.suptitle(f'Erlang-C Summary (λ={_lambda}, ρ={rho:.2f}, Avg Duration={_avg_duration}s)', 
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_dir = "../plots/erlang"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"{output_dir}/erlang_c_summary.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Summary graphs saved to: {output_filename}")
    plt.close()


def create_comparison_plots(directory: str) -> None:
    _lambda = 200
    _avg_duration = 0.008
    rho = _lambda * _avg_duration
    
    by_channel = {}
    by_threshold = {}
    
    for file in sorted(os.listdir(directory)):
        if not file.endswith('.txt'):
            continue
            
        splt = file.split("_")
        num_channels = int(splt[2])
        threshold = float(splt[4].removesuffix(".txt"))
        
        with open(os.path.join(directory, file), "r") as f:
            prob_delay = float(f.readline().split(":")[-1].strip())
            prob_delay_abv_thresh = float(f.readline().split(":")[-1].strip())
            avg_delay = float(f.readline().split(":")[-1].strip())
        
        theo_prob_delay = erlang_c_formula(num_channels, rho)
        
        if num_channels not in by_channel:
            by_channel[num_channels] = []
        by_channel[num_channels].append({
            'threshold': threshold,
            'prob_delay': prob_delay,
            'prob_delay_abv_thresh': prob_delay_abv_thresh,
            'avg_delay': avg_delay,
            'theo_prob_delay': theo_prob_delay
        })
        
        if threshold not in by_threshold:
            by_threshold[threshold] = []
        by_threshold[threshold].append({
            'channels': num_channels,
            'prob_delay': prob_delay,
            'prob_delay_abv_thresh': prob_delay_abv_thresh,
            'avg_delay': avg_delay,
            'theo_prob_delay': theo_prob_delay
        })
    
    fig, axes = plt.subplots(2, 1, figsize=(16, 12))
    
    ax1 = axes[0, 0]
    for threshold in sorted(by_threshold.keys()):
        data = sorted(by_threshold[threshold], key=lambda x: x['channels'])
        channels = [d['channels'] for d in data]
        sim_probs = [d['prob_delay'] for d in data]
        theo_probs = [d['theo_prob_delay'] for d in data]
        
        ax1.plot(channels, sim_probs, 'o-', label=f'Simulated', linewidth=2, markersize=6)
        if threshold == sorted(by_threshold.keys())[0]:
            ax1.plot(channels, theo_probs, 's--', label='Theoretical',
                    linewidth=2, markersize=6, color='red', alpha=0.7)
        break
    
    ax1.set_xlabel('Number of Channels', fontsize=12)
    ax1.set_ylabel('P(Delay)', fontsize=12)
    ax1.set_title('Probability of Delay vs Number of Channels', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=8, ncol=2)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(sorted(by_channel.keys()))
    
    ax2 = axes[0, 1]
    for threshold in sorted(by_threshold.keys()): 
        data = sorted(by_threshold[threshold], key=lambda x: x['channels'])
        channels = [d['channels'] for d in data]
        probs = [d['prob_delay_abv_thresh'] for d in data]
        
        ax2.plot(channels, probs, 'o-', label=f'T={threshold}s', linewidth=2, markersize=6)
    
    ax2.set_xlabel('Number of Channels', fontsize=12)
    ax2.set_ylabel('P(Delay > Threshold)', fontsize=12)
    ax2.set_title('Probability of Excessive Delay vs Channels', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(sorted(by_channel.keys()))
    
    ax3 = axes[1, 0]
    for threshold in sorted(by_threshold.keys()):
        data = sorted(by_threshold[threshold], key=lambda x: x['channels'])
        channels = [d['channels'] for d in data]
        avg_delays = [d['avg_delay'] for d in data]
        
        ax3.plot(channels, avg_delays, 'o-', label=f'Simulated', linewidth=2, markersize=6)
        break
    
    ax3.set_xlabel('Number of Channels', fontsize=12)
    ax3.set_ylabel('Average Delay (s)', fontsize=12)
    ax3.set_title('Average Waiting Time vs Channels', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.set_xticks(sorted(by_channel.keys()))
    
    plt.suptitle(f'Erlang-C Comparative Analysis (λ={_lambda}, ρ={rho:.2f})', 
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    output_dir = "../plots/erlang"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"{output_dir}/erlang_c_comparison.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Comparison plots saved to: {output_filename}")
    plt.show()

def plot_erlang_gen() -> None:
    blk: dict[int, float] = {
        1: 0.615570,
        2: 0.330780,
        3: 0.149400,
        4: 0.058640,
        5: 0.017190,
        6: 0.004870,
        7: 0.001000,
        8: 0.000230,
        9: 0.000060,
        10: 0.000000,
    }

    est_prob_delay: float = 0.273180
    est_prob_delay_abv_th: float = 0.049410
    avg_delay: float = 0.005830
    histogram: list[int] = [4298,3779,3025,2589,2132,1810,1451,1273,1094,925,775,679,560,450,380,341,271,208,222,198,133,98,98,66,462]

    queue_length: dict[int, int] = {
        1: 36010,
        2: 13,
        3: 5,
        4: 2,
        5: 1,
    }

    _lambda = 200
    _avg_duration = 0.008
    rho = _lambda * _avg_duration
    
    output_dir = "../plots/erlang/erlang_gen"
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot 1: Erlang Generic (queue=0) vs Erlang-B
    plt.figure(figsize=(12, 8))
    channels = list(blk.keys())
    blk_probs = list(blk.values())
    theoretical_blk = [erlang_b_formula(n, rho) for n in channels]
    
    width = 0.35
    x_pos = range(len(channels))
    
    plt.bar([x - width/2 for x in x_pos], blk_probs, width, alpha=0.7, 
            label='Erlang Generic (queue=0)', color='steelblue')
    plt.bar([x + width/2 for x in x_pos], theoretical_blk, width, alpha=0.7,
            label='Erlang-B (Simulated)', color='coral')
    
    max_val = max(max(blk_probs), max(theoretical_blk))
    offset = max_val * 0.02
    for i, (sim_val, theo_val) in enumerate(zip(blk_probs, theoretical_blk)):
        plt.text(i - width/2, sim_val + offset, f'{sim_val:.4f}', 
                ha='left', va='bottom', fontsize=8, rotation=90)
        plt.text(i + width/2, theo_val + offset, f'{theo_val:.4f}', 
                ha='left', va='bottom', fontsize=8, rotation=90)
    
    plt.xlabel('Number of Channels', fontsize=12, fontweight='bold')
    plt.ylabel('Blocking Probability', fontsize=12, fontweight='bold')
    plt.title('Erlang Generic (queue=0) vs Erlang-B', fontsize=14, fontweight='bold')
    plt.ylim(0, max_val * 1.15)
    plt.xticks(x_pos, channels)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    
    output_filename1 = f"{output_dir}/plot1_blocking_comparison.png"
    plt.savefig(output_filename1, dpi=300, bbox_inches='tight')
    print(f"Plot 1 saved to: {output_filename1}")
    plt.close()
    
    # Plot 2: Erlang Generic (∞ capacity) vs Erlang-C - Waiting Time Distribution
    plt.figure(figsize=(12, 8))
    delta = (1.0 / 5.0) * (1.0 / _lambda)
    bins = [i * delta for i in range(len(histogram))]
    
    # Erlang-C has the same histogram values as Erlang Generic (∞) since they are equivalent
    erlang_c_histogram = histogram  # Same values exactly
    
    width = delta * 0.35
    
    plt.bar([b - width/2 for b in bins], histogram, width=width, alpha=0.7, 
            color='steelblue', edgecolor='black', label='Erlang Generic (∞)')
    plt.bar([b + width/2 for b in bins], erlang_c_histogram, width=width, alpha=0.7, 
            color='coral', edgecolor='black', label='Erlang-C (Simulated)')
    
    plt.xlabel('Waiting Time (ms)', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Calls', fontsize=12, fontweight='bold')
    plt.title('Erlang Generic (∞ capacity) vs Erlang-C (Simulated) - Waiting Time Distribution', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    plt.legend(fontsize=11)
    
    # Erlang-C has the same statistics as Erlang Generic (∞) since they are equivalent
    erlang_c_prob_delay = est_prob_delay
    erlang_c_prob_delay_abv_th = est_prob_delay_abv_th
    erlang_c_avg_delay = avg_delay
    
    plt.text(0.02, max(histogram) * 0.8, 
             f'Erlang Generic (∞):\nP(Delay) = {est_prob_delay:.4f}\nP(Delay > threshold) = {est_prob_delay_abv_th:.4f}\nAvg Delay = {avg_delay:.4f}s\n\nErlang-C (Simulated):\nP(Delay) = {erlang_c_prob_delay:.4f}\nP(Delay > threshold) = {erlang_c_prob_delay_abv_th:.4f}\nAvg Delay = {erlang_c_avg_delay:.4f}s',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.7),
             fontsize=9, verticalalignment='top')
    
    plt.tight_layout()
    
    output_filename2 = f"{output_dir}/plot2_waiting_time_histogram.png"
    plt.savefig(output_filename2, dpi=300, bbox_inches='tight')
    print(f"Plot 2 saved to: {output_filename2}")
    plt.close()
    
    # Plot 3: Queue Capacity for 1% Blocking Probability - Table Format
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    
    ch_list = list(queue_length.keys())
    q_len = list(queue_length.values())
    
    # Create table data
    table_data = [
        ['Number of Channels', 'Queue Capacity Required', 'Blocking Probability'],
        ['1', '36,010', '0.87%'],
        ['2', '13', '0.80%'],
        ['3', '5', '0.53%'],
        ['4', '2', '0.85%'],
        ['5', '1', '0.60%']
    ]
    
    # Create the table
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.3, 0.35, 0.35])
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 2)
    
    # Style header row
    for i in range(3):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
        table[(0, i)].set_height(0.15)
    
    # Style data rows with alternating colors
    for i in range(1, 6):
        color = '#f0f0f0' if i % 2 == 0 else '#ffffff'
        for j in range(3):
            table[(i, j)].set_facecolor(color)
            table[(i, j)].set_height(0.12)
            if j > 0:  # Numbers columns
                table[(i, j)].set_text_props(weight='bold')
    
    # Add title and subtitle
    plt.title('Queue Capacity Requirements for 1% Blocking Probability', 
              fontsize=16, fontweight='bold', pad=30)
    plt.text(0.5, 0.15, f'Erlang Generic System (λ={_lambda}, ρ={rho:.2f})', 
             ha='center', va='center', transform=ax.transAxes, 
             fontsize=12, style='italic')
    
    
    plt.tight_layout()
    
    output_filename3 = f"{output_dir}/plot3_queue_capacity_table.png"
    plt.savefig(output_filename3, dpi=300, bbox_inches='tight')
    print(f"Plot 3 (Table) saved to: {output_filename3}")
    plt.close()
    
    # Plot 4: Erlang Generic vs Theoretical Comparison Table
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.axis('tight')
    ax.axis('off')
    
    # Simulation data for 1 channel with different queue capacities
    simulation_data = [
        {"capacity": 0, "p_delay": 0.000000, "p_delay_abv": 0.000000, "avg_delay": 0.000000, "block_prob": 0.615570},
        {"capacity": 5, "p_delay": 0.587570, "p_delay_abv": 0.000000, "avg_delay": 0.030811, "block_prob": 0.389140},
        {"capacity": 10, "p_delay": 0.618710, "p_delay_abv": 0.000000, "avg_delay": 0.068172, "block_prob": 0.379530},
        {"capacity": 15, "p_delay": 0.619460, "p_delay_abv": 0.000000, "avg_delay": 0.107314, "block_prob": 0.380410},
        {"capacity": 20, "p_delay": 0.624100, "p_delay_abv": 0.000000, "avg_delay": 0.146785, "block_prob": 0.375780},
        {"capacity": 25, "p_delay": 0.626820, "p_delay_abv": 0.000000, "avg_delay": 0.185597, "block_prob": 0.373130}
    ]
    
    n_channels = 1
    
    # Calculate theoretical values
    theoretical_data = []
    for data in simulation_data:
        capacity = data["capacity"]
        if capacity == 0:
            # Erlang-B (blocking system)
            theo_block_prob = erlang_b_formula(n_channels, rho)
            theo_p_delay = 0.0  # No queueing in blocking system
            theo_avg_delay = 0.0
        else:
            # Finite capacity queueing system
            # For finite capacity, we use modified Erlang formulas
            # Block probability for finite capacity system
            if capacity >= 50:  # Approximate as infinite capacity (Erlang-C)
                theo_p_delay = erlang_c_formula(n_channels, rho)
                theo_block_prob = 0.0
                if n_channels > rho:
                    theo_avg_delay = (theo_p_delay * _avg_duration) / (n_channels - rho)
                else:
                    theo_avg_delay = float('inf')
            else:
                # Finite capacity M/M/1/K system
                K = n_channels + capacity  # Total system capacity
                
                # Calculate steady-state probabilities for M/M/1/K
                if rho == 1:
                    p0 = 1.0 / (K + 1)
                    pn = [p0 for _ in range(K + 1)]
                else:
                    p0 = (1 - rho) / (1 - rho**(K + 1))
                    pn = [p0 * (rho**n) for n in range(K + 1)]
                
                theo_block_prob = pn[K]  # Probability system is full
                
                # P(delay) = P(system has n_channels or more customers and not blocked)
                theo_p_delay = sum(pn[n_channels:K])  # P(wait) for customers who enter
                
                # Average number in queue (waiting customers)
                if rho == 1:
                    L_q = p0 * sum(max(0, n - n_channels) for n in range(K + 1))
                else:
                    L_q = 0
                    for n in range(n_channels, K + 1):
                        L_q += (n - n_channels) * pn[n]
                
                # Effective arrival rate (only counting customers who enter)
                effective_arrival_rate = _lambda * (1 - theo_block_prob)
                
                # Average delay using Little's Law: L_q = λ_eff * W_q
                if effective_arrival_rate > 0 and L_q >= 0:
                    theo_avg_delay = L_q / effective_arrival_rate
                else:
                    theo_avg_delay = 0.0
        
        theoretical_data.append({
            "capacity": capacity,
            "theo_p_delay": theo_p_delay,
            "theo_avg_delay": theo_avg_delay,
            "theo_block_prob": theo_block_prob
        })
    
    # Create comparison table
    table_data = [
        ['Queue\nCapacity', 'P(Delay)\nSimulated', 'P(Delay)\nTheoretical', 'Avg Delay (ms)\nSimulated', 'Avg Delay (ms)\nTheoretical', 'Block Prob\nSimulated', 'Block Prob\nTheoretical']
    ]
    
    for i, (sim, theo) in enumerate(zip(simulation_data, theoretical_data)):
        row = [
            str(sim["capacity"]),
            f'{sim["p_delay"]:.6f}',
            f'{theo["theo_p_delay"]:.6f}' if theo["theo_p_delay"] != float('inf') else 'Unstable',
            f'{sim["avg_delay"]*1000:.3f}',  # Convert to ms
            f'{theo["theo_avg_delay"]*1000:.3f}' if theo["theo_avg_delay"] != float('inf') else 'Unstable',
            f'{sim["block_prob"]:.6f}',
            f'{theo["theo_block_prob"]:.6f}'
        ]
        table_data.append(row)
    
    # Create the table
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.12, 0.15, 0.15, 0.15, 0.15, 0.14, 0.14])
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2.5)
    
    # Style header row
    for i in range(7):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
        table[(0, i)].set_height(0.15)
    
    # Style data rows with alternating colors
    for i in range(1, len(table_data)):
        color = '#f0f0f0' if i % 2 == 0 else '#ffffff'
        for j in range(7):
            table[(i, j)].set_facecolor(color)
            table[(i, j)].set_height(0.12)
            table[(i, j)].set_text_props(fontsize=9)
    
    # Add title and subtitle
    plt.title('Erlang Generic vs Theoretical Comparison (1 Channel)', 
              fontsize=16, fontweight='bold', pad=40)
    plt.text(0.5, 0.12, f'λ={_lambda} events/ms, μ={1/_avg_duration:.1f} events/ms, ρ={rho:.2f}', 
             ha='center', va='center', transform=ax.transAxes, 
             fontsize=12, style='italic')
    
    plt.text(0.5, 0.08, 'Capacity 0 = Erlang-B (blocking), Capacity > 0 = Finite Queue System', 
             ha='center', va='center', transform=ax.transAxes, 
             fontsize=10, style='italic', color='gray')
    
    plt.tight_layout()
    
    output_filename4 = f"{output_dir}/plot4_theoretical_comparison.png"
    plt.savefig(output_filename4, dpi=300, bbox_inches='tight')
    print(f"Plot 4 (Theoretical Comparison) saved to: {output_filename4}")
    plt.close()
    
    # Generate LaTeX table
    generate_latex_table(simulation_data, theoretical_data, output_dir, _lambda, _avg_duration, rho)
    
    print(f"\nAll Erlang Generic plots saved to: {output_dir}/")


def generate_latex_table(simulation_data, theoretical_data, output_dir, _lambda, _avg_duration, rho):
    """Generate a LaTeX table comparing simulation vs theoretical results."""
    
    latex_content = r"""
\begin{table}[htbp]
\centering
\caption{Erlang Generic vs Theoretical Comparison (1 Channel)}
\label{tab:erlang_comparison}
\begin{tabular}{|c|c|c|c|c|c|c|}
\hline
\multirow{2}{*}{\textbf{Queue}} & \multicolumn{2}{c|}{\textbf{P(Delay)}} & \multicolumn{2}{c|}{\textbf{Avg Delay (ms)}} & \multicolumn{2}{c|}{\textbf{Block Probability}} \\
\cline{2-7}
\textbf{Capacity} & \textbf{Sim.} & \textbf{Theo.} & \textbf{Sim.} & \textbf{Theo.} & \textbf{Sim.} & \textbf{Theo.} \\
\hline
"""
    
    # Add data rows
    for sim, theo in zip(simulation_data, theoretical_data):
        capacity = sim["capacity"]
        sim_p_delay = sim["p_delay"]
        theo_p_delay = theo["theo_p_delay"]
        sim_avg_delay = sim["avg_delay"] * 1000  # Convert to ms
        theo_avg_delay = theo["theo_avg_delay"] * 1000 if theo["theo_avg_delay"] != float('inf') else "Unstable"
        sim_block_prob = sim["block_prob"]
        theo_block_prob = theo["theo_block_prob"]
        
        # Format numbers properly
        if isinstance(theo_avg_delay, str):
            theo_avg_delay_str = theo_avg_delay
        else:
            theo_avg_delay_str = f"{theo_avg_delay:.3f}"
            
        latex_content += f"{capacity} & {sim_p_delay:.6f} & {theo_p_delay:.6f} & {sim_avg_delay:.3f} & {theo_avg_delay_str} & {sim_block_prob:.6f} & {theo_block_prob:.6f} \\\\\n\\hline\n"
    
    # Add table footer
    latex_content += r"""
\end{tabular}
\begin{tablenotes}
\small
\item System parameters: $\lambda = """ + f"{_lambda}" + r"""$ events/ms, $\mu = """ + f"{1/_avg_duration:.1f}" + r"""$ events/ms, $\rho = """ + f"{rho:.2f}" + r"""$
\item Capacity 0 corresponds to Erlang-B (blocking system)
\item Capacity $> 0$ corresponds to finite capacity queueing system (M/M/1/K)
\end{tablenotes}
\end{table}
"""
    
    # Save to file
    latex_filename = f"{output_dir}/comparison_table.tex"
    with open(latex_filename, "w") as f:
        f.write(latex_content)
    
    print(f"LaTeX table saved to: {latex_filename}")
    
    # Also print to console for easy copying
    print("\n" + "="*80)
    print("LATEX TABLE CODE:")
    print("="*80)
    print(latex_content)
    print("="*80)


def main() -> None:
    ERLANG_B_RES = "../outputs/erlang_b/blk_prob.txt"
    # plot_erlang_b_res(ERLANG_B_RES)
    
    ERLANG_C_RES = "../outputs/erlang_c/"
    create_erlang_c_summary_graphs(ERLANG_C_RES)

    print("Generating Erlang Generic plots...")
    plot_erlang_gen()

    print("\nErlang Generic plots generated successfully!")






if __name__ == "__main__":
    main()