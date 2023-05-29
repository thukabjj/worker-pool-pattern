import pandas as pd
import matplotlib.pyplot as plt

# Read the results from CSV files
java_results = pd.read_csv('java_results.csv')
go_results = pd.read_csv('go_results.csv')

# Convert execution time from milliseconds to seconds
java_results['Execution Time'] /= 1000
go_results['Execution Time'] /= 1000

# Calculate Memory Usage Difference
java_results['Memory Usage Difference'] = java_results['Memory Usage End'] - java_results['Memory Usage Begin']
go_results['Memory Usage Difference'] = go_results['Memory Usage End'] - go_results['Memory Usage Begin']

# Create subplots
fig, axs = plt.subplots(3, 1)
fig.suptitle('Java vs Go Worker Pool Performance')

# Plot Execution Time
axs[0].plot(java_results['Execution Time'], label='Java')
axs[0].plot(go_results['Execution Time'], label='Go')
axs[0].set_title('Execution Time (s)')
axs[0].legend()

# Plot CPU Usage
axs[1].plot(java_results['CPU Usage'], label='Java')
axs[1].plot(go_results['CPU Usage'], label='Go')
axs[1].set_title('CPU Usage (%)')
axs[1].legend()

# Plot Memory Usage Difference
axs[2].plot(java_results['Memory Usage Difference'], label='Java')
axs[2].plot(go_results['Memory Usage Difference'], label='Go')
axs[2].set_title('Memory Usage Difference (bytes)')
axs[2].legend()

# Show the plot
plt.tight_layout()
plt.show()
