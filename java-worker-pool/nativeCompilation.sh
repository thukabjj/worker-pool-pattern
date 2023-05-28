#! /bin/bash

javac -d build src/main/java/com/github/thukabjj/javaworkerpool/WorkerPoolPattern.java

jar cfvm WorkerPoolPattern.jar META-INF/MANIFEST.MF -C build .

native-image -jar WorkerPoolPattern.jar