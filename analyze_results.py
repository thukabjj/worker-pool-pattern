import pandas as pd
import matplotlib.pyplot as plt

# Read the results from CSV files
java_results = pd.read_csv('java_results.csv')
go_results = pd.read_csv('go_results.csv')
java_summary = pd.read_csv('java_summary.csv')
go_summary = pd.read_csv('go_summary.csv')

# Ensure Memory Usage column exists and calculate Memory Usage Difference
if 'Memory Usage' in java_results.columns:
    java_results['Memory Usage Difference'] = java_results['Memory Usage']
if 'Memory Usage' in go_results.columns:
    go_results['Memory Usage Difference'] = go_results['Memory Usage']

# Compute averages and standard deviations
java_avg_time = java_summary[java_summary['Metric'] == 'Execution Time']['Average'].values[0]
go_avg_time = go_summary[go_summary['Metric'] == 'Execution Time']['Average'].values[0]
java_std_time = java_summary[java_summary['Metric'] == 'Execution Time']['StdDev'].values[0]
go_std_time = go_summary[go_summary['Metric'] == 'Execution Time']['StdDev'].values[0]

# Create subplots with error bars
fig, axs = plt.subplots(3, 1, figsize=(10, 15))
fig.suptitle('Java vs Go Worker Pool Performance')

# Plot Execution Time with error bars
axs[0].errorbar(range(len(java_results)), java_results['Execution Time'], yerr=java_std_time, fmt='-o', label='Java')
axs[0].errorbar(range(len(go_results)), go_results['Execution Time'], yerr=go_std_time, fmt='-o', label='Go')
axs[0].axhline(y=java_avg_time, color='blue', linestyle='--', label='Java Average')
axs[0].axhline(y=go_avg_time, color='orange', linestyle='--', label='Go Average')
axs[0].set_title('Execution Time (s)')
axs[0].legend()

# Plot CPU Usage with average lines
java_avg_cpu = java_summary[java_summary['Metric'] == 'CPU Usage']['Average'].values[0]
go_avg_cpu = go_summary[go_summary['Metric'] == 'CPU Usage']['Average'].values[0]
axs[1].plot(java_results['CPU Usage'], label='Java')
axs[1].plot(go_results['CPU Usage'], label='Go')
axs[1].axhline(y=java_avg_cpu, color='blue', linestyle='--', label='Java Average')
axs[1].axhline(y=go_avg_cpu, color='orange', linestyle='--', label='Go Average')
axs[1].set_title('CPU Usage (%)')
axs[1].legend()

# Plot Memory Usage Difference with average lines, if available
if 'Memory Usage Difference' in java_results.columns and 'Memory Usage Difference' in go_results.columns:
    java_avg_mem = java_summary[java_summary['Metric'] == 'Memory Usage']['Average'].values[0]
    go_avg_mem = go_summary[go_summary['Metric'] == 'Memory Usage']['Average'].values[0]
    axs[2].plot(java_results['Memory Usage Difference'], label='Java')
    axs[2].plot(go_results['Memory Usage Difference'], label='Go')
    axs[2].axhline(y=java_avg_mem, color='blue', linestyle='--', label='Java Average')
    axs[2].axhline(y=go_avg_mem, color='orange', linestyle='--', label='Go Average')
    axs[2].set_title('Memory Usage (bytes)')
    axs[2].legend()

# Save the plot to file
plt.tight_layout()
plt.savefig('Java_vs_Go_Performance.png')
plt.show()
