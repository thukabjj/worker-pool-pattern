import subprocess
import pandas as pd

iterations = 100

java_command = ["java", "-jar", "java-worker-pool/WorkerPoolPattern.jar"]

java_times = []
java_cpu_usages = []
java_mem_usages_begin = []
java_mem_usages_end = []

for i in range(iterations):
    output = subprocess.check_output(java_command, universal_newlines=True).split('\n')

    time_str = output[0].split(":")[1].strip()
    if 'ms' in time_str:
        time_str = time_str.replace('ms', '')
        java_times.append(float(time_str) / 1000)
    elif 's' in time_str:
        time_str = time_str.replace('s', '')
        java_times.append(float(time_str))

    cpu_usage_str = output[1].split(":")[1].strip()
    cpu_usage_str = cpu_usage_str.replace('%', '')
    java_cpu_usages.append(float(cpu_usage_str))

    mem_usage_begin_str = output[2].split(":")[1].strip()
    mem_usage_begin_str = mem_usage_begin_str.replace(' bytes', '')
    java_mem_usages_begin.append(int(mem_usage_begin_str))

    mem_usage_end_str = output[3].split(":")[1].strip()
    mem_usage_end_str = mem_usage_end_str.replace(' bytes', '')
    java_mem_usages_end.append(int(mem_usage_end_str))

df = pd.DataFrame({
    'Execution Time': java_times,
    'CPU Usage': java_cpu_usages,
    'Memory Usage Begin': java_mem_usages_begin,
    'Memory Usage End': java_mem_usages_end
})

df.to_csv('java_results.csv', index=False)
