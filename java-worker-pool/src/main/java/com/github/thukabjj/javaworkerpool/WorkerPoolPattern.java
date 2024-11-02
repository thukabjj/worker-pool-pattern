package main.java.com.github.thukabjj.javaworkerpool;

import com.sun.management.OperatingSystemMXBean;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.lang.management.ManagementFactory;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.*;

public class WorkerPoolPattern {

    private static final Set<Integer> REQUIRED_FIELDS = new HashSet<>(Arrays.asList(0, 3));
    private static final BlockingQueue<String> errorLines = new LinkedBlockingQueue<>(500); // Larger queue for error buffering
    private static final int BATCH_SIZE = 100;

    public static void main(String[] args) throws IOException, InterruptedException {
        Path csvFile = Paths.get("./data_100000.csv");

        long cpuStart = measureCpuUsage();
        long memStart = measureMemoryUsage();
        long startTime = System.currentTimeMillis();

        int availableProcessors = Runtime.getRuntime().availableProcessors();
        ExecutorService executor = Executors.newFixedThreadPool(availableProcessors); // Efficient thread pool

        try (BufferedReader reader = Files.newBufferedReader(csvFile)) {
            String line;
            while ((line = reader.readLine()) != null) {
                final String currentLine = line;
                executor.submit(() -> processLine(currentLine));
            }
        }
        executor.shutdown();
        executor.awaitTermination(1, TimeUnit.HOURS); // Wait for all tasks to complete

        writeErrorLinesToFile();

        long cpuEnd = measureCpuUsage();
        long memEnd = measureMemoryUsage();
        long endTime = System.currentTimeMillis();

        System.out.printf("Execution Time: %d ms%n", (endTime - startTime));
        System.out.printf("CPU Usage: %.2f%%%n", (cpuEnd - cpuStart) * 100.0);
        System.out.printf("Memory Usage Begin: %d bytes%n", memStart);
        System.out.printf("Memory Usage End: %d bytes%n", memEnd);
        System.out.printf("Memory Usage Difference: %d bytes%n", (memEnd - memStart));
    }

    private static void processLine(String line) {
        String[] fields = line.split(",");
        boolean hasError = REQUIRED_FIELDS.stream().anyMatch(fieldPos ->
            fields.length <= fieldPos || fields[fieldPos].isEmpty()
        );
        if (hasError) {
            errorLines.offer(line + ", error: missing required field(s)");
        }
    }

    private static void writeErrorLinesToFile() throws IOException {
        try (BufferedWriter writer = Files.newBufferedWriter(Paths.get("errors.csv"))) {
            StringBuilder batch = new StringBuilder();
            int count = 0;
            while (!errorLines.isEmpty() || count > 0) {
                try {
                    String line = errorLines.poll(50, TimeUnit.MILLISECONDS); // Timed poll to avoid blocking
                    if (line != null) {
                        batch.append(line).append(System.lineSeparator());
                        count++;
                    }
                    if (count >= BATCH_SIZE || line == null) {
                        writer.write(batch.toString());
                        batch.setLength(0); // Reset for the next batch
                        count = 0;
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt(); // Handle interrupted status
                }
            }
            if (batch.length() > 0) {
                writer.write(batch.toString());
            }
        }
    }
    
    private static long measureCpuUsage() {
        OperatingSystemMXBean osBean = (OperatingSystemMXBean) ManagementFactory.getOperatingSystemMXBean();
        int cores = Runtime.getRuntime().availableProcessors();
        return (long) ((osBean.getProcessCpuLoad() * 100) / cores); // Normalize by core count
    }
    

    private static long measureMemoryUsage() {
        return Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory();
    }
}
