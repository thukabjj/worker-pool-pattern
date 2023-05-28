# README

## Worker Pool Pattern in Java and Go

This project demonstrates the Worker Pool Pattern implemented in both Java and Go programming languages. The primary objective of this project is to compare the efficiency of both implementations concerning CPU usage, memory footprint, and execution time.

The application is designed to handle large text files with hundreds of thousands of lines efficiently. The text file is read line by line and divided into tasks, each containing a set of lines. These tasks are then processed by worker threads (in Java) or goroutines (in Go) as part of a worker pool.

## Project Goals

- Implement the Worker Pool Pattern in both Java and Go
- Efficiently process large files
- Compare the CPU usage, memory footprint, and execution time of both implementations

## Features

- Worker Pool Pattern for optimal CPU utilization
- Concurrency with thread safety in both Java and Go
- Efficient handling of large files
- Header validation in the file processing

## Prerequisites

- Java 17
- GraalVM
- Native Image GraalVM component
- Go 1.16 or later

## Building the Project

1. **Compile the Java files and create a native image:**

    ```bash
    javac -d build src/main/java/com/github/thukabjj/javaworkerpool/WorkerPoolPattern.java
    jar cfvm WorkerPoolPattern.jar META-INF/MANIFEST.MF -C build .
    native-image -jar WorkerPoolPattern.jar
    ```

    This series of commands compile the Java source files, packages them into a JAR file, and then uses GraalVM's `native-image` tool to compile the JAR file into a native executable.

2. **Compile the Go files:**

    ```bash
    go build -o worker_pool_pattern_go main.go
    ```

    This command compiles the Go source files into an executable binary.

## Running the Project

After building the project, you can run the resulting native image and binary as you would run any other executable:

```bash
./WorkerPoolPattern
./worker_pool_pattern_go
```

## Analysis

To analyze the performance of both implementations, consider the following metrics:

- CPU usage: Measure the amount of CPU resources consumed by each implementation.
- Memory footprint: Monitor the memory consumption of both implementations.
- Execution time: Measure the time it takes for each implementation to process the file.

Please note that the current file path is hardcoded. You may need to modify it in the source code to match your environment.

## License

This project is open source and available under the [MIT License](LICENSE).


## Show your support

Give a ⭐️ if this project helped you!

----
This README was generated with ❤️ by [Arthur Costa]