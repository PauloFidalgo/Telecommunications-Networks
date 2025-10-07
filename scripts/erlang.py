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
    ax2.set_ylabel('Time (seconds)', fontsize=11)
    ax2.set_title('Average Waiting Time (for delayed calls)', fontsize=12, fontweight='bold')
    ax2.set_xticks(x_pos2)
    ax2.set_xticklabels(delays)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    ax3 = axes[1, 0]
    delta = (1.0 / 5.0) * (1.0 / _lambda)
    bins = [i * delta for i in range(len(_histogram))]
    
    ax3.bar(bins, _histogram, width=delta*0.8, alpha=0.7, color='steelblue', edgecolor='black')
    ax3.set_xlabel('Waiting Time (seconds)', fontsize=11)
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
            theo_avg_delays.append(0)
    
    ax2.bar([x - width/2 for x in x_pos], sim_avg_delays, width, alpha=0.7, 
            label='Simulated', color='steelblue')
    ax2.bar([x + width/2 for x in x_pos], theo_avg_delays, width, alpha=0.7,
            label='Theoretical', color='coral')
    
    max_delay_val = max([v for v in sim_avg_delays + theo_avg_delays if v > 0])
    delay_offset = max_delay_val * 0.02
    for i, (sim_val, theo_val) in enumerate(zip(sim_avg_delays, theo_avg_delays)):
        ax2.text(i - width/2, sim_val + delay_offset, f'{sim_val:.3f}', 
                ha='left', va='bottom', fontsize=8, rotation=90)
        if theo_val > 0:
            ax2.text(i + width/2, theo_val + delay_offset, f'{theo_val:.3f}', 
                    ha='left', va='bottom', fontsize=8, rotation=90)
    
    ax2.set_xlabel('Number of Channels', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Average Delay (seconds)', fontsize=12, fontweight='bold')
    ax2.set_title('Average Waiting Time vs Number of Channels', fontsize=13, fontweight='bold')
    max_delay = max([v for v in sim_avg_delays + theo_avg_delays if v > 0])
    ax2.set_ylim(0, max_delay * 1.15)
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
        
        ax3.plot(channels_list, probs, 'o-', label=f'T = {threshold}s', 
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


def main() -> None:
    ERLANG_B_RES = "../outputs/erlang_b/blk_prob.txt"

    ERLANG_C_RES = "../outputs/erlang_c/"
    
    print("Generating summary graphs...")
    create_erlang_c_summary_graphs(ERLANG_C_RES)
    
    print("\nSummary plots generated successfully!")




if __name__ == "__main__":
    main()