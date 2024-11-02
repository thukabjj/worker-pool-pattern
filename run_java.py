import subprocess
import pandas as pd
import numpy as np
import psutil
import time

# Configuration
iterations = 100
warmup_iterations = 10

# Command to run the Java native image
java_command = ["./java-worker-pool/WorkerPoolPattern"]

# Metric lists
java_times = []
java_cpu_usages = []
java_mem_usages = []

# Warm-up phase
for i in range(warmup_iterations):
    subprocess.run(java_command, check=True)

# Actual measurement phase
for i in range(iterations):
    print(f"Running iteration {i + 1}")

    # Start the Java process
    process = subprocess.Popen(java_command)
    proc = psutil.Process(process.pid)

    # Initialize variables for resource tracking
    cpu_usage_samples = []
    mem_usage_samples = []
    start_time = time.time()

    try:
        # Monitor CPU and memory usage while the process runs
        while process.poll() is None:  # While the process is running
            try:
                cpu_usage_samples.append(proc.cpu_percent(interval=0.1))  # CPU % over 0.1 seconds
                mem_usage_samples.append(proc.memory_info().rss)  # Memory in bytes
            except psutil.ZombieProcess:
                print(f"Warning: Process {process.pid} became a zombie during iteration {i + 1}.")
                break  # Exit monitoring if the process is a zombie
            time.sleep(0.1)  # Sampling interval
    except psutil.NoSuchProcess:
        print(f"Warning: Process {process.pid} no longer exists.")
    
    # Capture total execution time
    end_time = time.time()
    java_times.append(end_time - start_time)

    # Calculate average CPU and memory usage for this iteration if we collected any samples
    if cpu_usage_samples:
        avg_cpu_usage = np.mean(cpu_usage_samples)
    else:
        avg_cpu_usage = 0  # No data collected

    if mem_usage_samples:
        avg_mem_usage = np.mean(mem_usage_samples)
    else:
        avg_mem_usage = 0  # No data collected

    java_cpu_usages.append(avg_cpu_usage)
    java_mem_usages.append(avg_mem_usage)

    print(f"Iteration {i + 1} - Execution Time: {java_times[-1]} s, CPU Usage: {avg_cpu_usage:.2f}%, Memory Usage: {avg_mem_usage / 1024:.2f} KB")

# Compute statistical metrics
stats = {
    'Execution Time': java_times,
    'CPU Usage': java_cpu_usages,
    'Memory Usage': java_mem_usages
}

summary = {
    'Metric': ['Execution Time', 'CPU Usage', 'Memory Usage'],
    'Average': [np.mean(java_times), np.mean(java_cpu_usages), np.mean(java_mem_usages)],
    'StdDev': [np.std(java_times), np.std(java_cpu_usages), np.std(java_mem_usages)]
}

# Save raw data and summary statistics to CSV
df = pd.DataFrame(stats)
df.to_csv('java_results.csv', index=False)

summary_df = pd.DataFrame(summary)
summary_df.to_csv('java_summary.csv', index=False)
