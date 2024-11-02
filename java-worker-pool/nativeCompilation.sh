#!/bin/bash

# Remove previous builds if they exist
rm -rf WorkerPoolPattern.jar build

# Ensure the build directory exists
mkdir -p build

# Compile the Java code into the build directory
javac -d build src/main/java/com/github/thukabjj/javaworkerpool/WorkerPoolPattern.java

# Package the JAR with the manifest file
jar cfvm WorkerPoolPattern.jar META-INF/MANIFEST.MF -C build .

# Ensure the JAR file exists at the correct path
if [[ -f WorkerPoolPattern.jar ]]; then
    native-image -jar WorkerPoolPattern.jar
else
    echo "Error: WorkerPoolPattern.jar not found!"
    exit 1
fi
