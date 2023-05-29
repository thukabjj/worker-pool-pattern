import subprocess
import pandas as pd
import numpy as np

iterations = 100

go_command = ["./golang-worker-pool/main"]

go_times = []
go_cpu_usages = []
go_mem_usages_begin = []
go_mem_usages_end = []

for i in range(iterations):
    output = subprocess.check_output(go_command, universal_newlines=True).split('\n')

    time_str = output[0].split(":")[1].strip()
    if 'ms' in time_str:
        time_str = time_str.replace('ms', '')
        go_times.append(float(time_str) / 1000)
    elif 's' in time_str:
        time_str = time_str.replace('s', '')
        go_times.append(float(time_str))

    cpu_usage_str = output[1].split(":")[1].strip()
    cpu_usage_str = cpu_usage_str.replace('%', '')
    go_cpu_usages.append(float(cpu_usage_str))

    mem_usage_begin_str = output[2].split(":")[1].strip()
    mem_usage_begin_str = mem_usage_begin_str.replace(' bytes', '')
    go_mem_usages_begin.append(int(mem_usage_begin_str))

    mem_usage_end_str = output[3].split(":")[1].strip()
    mem_usage_end_str = mem_usage_end_str.replace(' bytes', '')
    go_mem_usages_end.append(int(mem_usage_end_str))


df = pd.DataFrame({
    'Execution Time': go_times,
    'CPU Usage': go_cpu_usages,
    'Memory Usage Begin': go_mem_usages_begin,
    'Memory Usage End': go_mem_usages_end
})

df.to_csv('go_results.csv', index=False)
