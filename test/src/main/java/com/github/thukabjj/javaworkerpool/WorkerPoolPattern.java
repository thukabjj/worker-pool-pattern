package main.java.com.github.thukabjj.javaworkerpool;
import com.sun.management.OperatingSystemMXBean;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class WorkerPoolPattern {

    private static final Set<Integer> REQUIRED_FIELDS = new HashSet<>(Arrays.asList(0, 3));
    private static final ConcurrentLinkedQueue<String> errorLines = new ConcurrentLinkedQueue<>();

    public static void main(String[] args) throws IOException, InterruptedException {
        Path csvFile = Paths.get("../data_100000.csv");
        ExecutorService executor = Executors.newFixedThreadPool(10);

        long cpuStart = measureCpuUsage();
        long memStart = measureMemoryUsage();

        long startTime = System.currentTimeMillis();

        try (BufferedReader reader = Files.newBufferedReader(csvFile)) {
            String line;
            while ((line = reader.readLine()) != null) {
                final String currentLine = line; // Declare final reference variable
                executor.execute(() -> processLine(currentLine));
            }
        }

        executor.shutdown();
        executor.awaitTermination(Long.MAX_VALUE, TimeUnit.NANOSECONDS);

        writeErrorLinesToFile();

        long cpuEnd = measureCpuUsage();
        long memEnd = measureMemoryUsage();

        long endTime = System.currentTimeMillis();
        long executionTime = endTime - startTime;

        System.out.println("Execution Time: " + executionTime + " ms");
        System.out.println("CPU Usage: " + (cpuEnd - cpuStart) + " %");
        System.out.println("Memory Used in the begin: " +  memStart + " bytes");
        System.out.println("Memory Usage: " + (memEnd - memStart) + " bytes");
    }


    private static void processLine(String line) {
        String[] fields = line.split(",");
        boolean hasError = false;
        for (int fieldPos : REQUIRED_FIELDS) {
            if (fields.length <= fieldPos || fields[fieldPos].isEmpty()) {
                hasError = true;
                break;
            }
        }
        if (hasError) {
            errorLines.add(line + ", error: missing required field(s)");
        }
    }

    private static void writeErrorLinesToFile() throws IOException {
        if (!errorLines.isEmpty()) {
            try (BufferedWriter writer = new BufferedWriter(new FileWriter("errors.csv"))) {
                while (!errorLines.isEmpty()) {
                    writer.write(errorLines.poll());
                    writer.newLine();
                }
            }
        }
    }

    private static long measureCpuUsage() {
        OperatingSystemMXBean osBean = (OperatingSystemMXBean) ManagementFactory.getOperatingSystemMXBean();
        return (long) (osBean.getProcessCpuLoad() * 100);
    }

    private static long measureMemoryUsage() {
        Runtime runtime = Runtime.getRuntime();
        return runtime.totalMemory() - runtime.freeMemory();
    }
}
