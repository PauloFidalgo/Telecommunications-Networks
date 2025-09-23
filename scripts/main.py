import matplotlib.pyplot as plt
import os
import numpy as np


def main() -> None:
    os.makedirs("../plots", exist_ok=True)

    for file in os.listdir("../outputs/"):
        if file.endswith(".txt"):
            with open(f"../outputs/{file}", "r") as f:
                avg_line = f.readline().strip()
                theoretical_line = f.readline().strip()
                lb_line = f.readline().strip()
                n_sample_line = f.readline().strip()
                hist_line = f.readline().strip()

                avg = float(avg_line.split(": ")[1])
                theoretical = float(theoretical_line.split(": ")[1])
                lb = int(lb_line.split(": ")[1])
                n_sample = int(n_sample_line.split(": ")[1])
                hist_data = hist_line.split(": ")[1]
                histogram = list(map(int, hist_data.split(",")))

                delta = (1.0 / 5.0) * (1.0 / lb)
                v_max = 5.0 * (1.0 / lb)

                x_values = np.arange(0, len(histogram)) * delta

                plt.figure(figsize=(12, 8))
                
                plt.bar(x_values, histogram, width=delta*0.8, alpha=0.7, 
                    label=f'Histogram (λ={lb}, N={n_sample})')
                
                plt.axvline(x=avg, color='red', linestyle='--', linewidth=2, 
                        label=f'Estimated Avg: {avg:.3f}')
                plt.axvline(x=theoretical, color='green', linestyle='--', linewidth=2, 
                        label=f'Theoretical Avg: {theoretical:.3f}')
                
                plt.title(f'Poisson Process Histogram\nλ={lb}, Samples={n_sample}', fontsize=14)
                plt.xlabel('Inter-arrival Time', fontsize=12)
                plt.ylabel('Frequency', fontsize=12)
                plt.legend()
                plt.grid(True, alpha=0.3)

                stats_text = f'Estimated: {avg:.3f}\nTheoretical: {theoretical:.3f}\nError: {abs(avg-theoretical):.3f}'
                plt.text(0.7, 0.95, stats_text, transform=plt.gca().transAxes, 
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"), 
                        verticalalignment='top')

                plot_filename = f"plots/{file.replace('.txt', '_histogram.png')}"
                plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
                plt.close()  
                
                print(f"Saved plot: {plot_filename}")

    print("All histogram plots have been generated and saved to 'plots/' directory!")


if __name__ == "__main__":
    main()
