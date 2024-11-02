import subprocess
import pandas as pd
import numpy as np
import psutil
import time

# Configuration
iterations = 100
warmup_iterations = 10

# Command to run the Go program
go_command = ["./golang-worker-pool/worker_pool_pattern_go"]


# Metric lists
go_times = []
go_cpu_usages = []
go_mem_usages = []

# Warm-up phase
for i in range(warmup_iterations):
    subprocess.run(go_command, check=True)

# Actual measurement phase
for i in range(iterations):
    print(f"Running iteration {i + 1}")

    # Start the process
    process = subprocess.Popen(go_command)
    proc = psutil.Process(process.pid)

    # Initialize variables for resource tracking
    cpu_usage_samples = []
    mem_usage_samples = []
    start_time = time.time()

    # Monitor CPU and memory usage while the process runs
    while process.poll() is None:  # While the process is running
        try:
            cpu_usage_samples.append(proc.cpu_percent(interval=0.1))  # CPU % over 0.1 seconds
            mem_usage_samples.append(proc.memory_info().rss)  # Memory in bytes
        except psutil.NoSuchProcess:
            break  # Exit if process terminates

        time.sleep(0.1)  # Sampling interval

    # Capture total execution time
    end_time = time.time()
    go_times.append(end_time - start_time)

    # Calculate average CPU and memory usage for this iteration
    avg_cpu_usage = np.mean(cpu_usage_samples) if cpu_usage_samples else 0
    avg_mem_usage = np.mean(mem_usage_samples) if mem_usage_samples else 0

    go_cpu_usages.append(avg_cpu_usage)
    go_mem_usages.append(avg_mem_usage)

    print(f"Iteration {i + 1} - Execution Time: {go_times[-1]} s, CPU Usage: {avg_cpu_usage:.2f}%, Memory Usage: {avg_mem_usage / 1024:.2f} KB")

# Compile results into DataFrames and save to CSV
stats = {
    'Execution Time': go_times,
    'CPU Usage': go_cpu_usages,
    'Memory Usage': go_mem_usages  # Ensure column name consistency
}

summary = {
    'Metric': ['Execution Time', 'CPU Usage', 'Memory Usage'],
    'Average': [np.mean(go_times), np.mean(go_cpu_usages), np.mean(go_mem_usages)],
    'StdDev': [np.std(go_times), np.std(go_cpu_usages), np.std(go_mem_usages)]
}

# Save raw data and summary statistics to CSV
df = pd.DataFrame(stats)
df.to_csv('go_results.csv', index=False)

summary_df = pd.DataFrame(summary)
summary_df.to_csv('go_summary.csv', index=False)
