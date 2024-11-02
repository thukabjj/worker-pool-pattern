package main

import (
	"bufio"
	"fmt"
	"io"
	"log"
	"net/http"
	_ "net/http/pprof" // Import pprof for profiling
	"os"
	"runtime"
	"strings"
	"sync"
	"time"
)

const (
	LinesPerWorker = 1000
	ErrorBatchSize = 100
)

var requiredFields = map[int]bool{0: true, 3: true}

type ErrorLine struct {
	Line  string
	Error error
}

var (
	errorFile *os.File
	errorBuf  *bufio.Writer
	errorChan = make(chan ErrorLine, 100)
)

func main() {
	// Start pprof in a separate goroutine
	go func() {
		log.Println(http.ListenAndServe("localhost:6060", nil))
	}()

	const fileName = "./data_100000.csv"

	file, err := os.Open(fileName)
	if err != nil {
		log.Fatalf("cannot open file: %v", err)
	}
	defer file.Close()

	go handleErrors() // Separate goroutine for handling errors

	cpuStart := measureCPUUsage()
	memStart := measureMemoryUsage()
	startTime := time.Now()

	processFile(file)

	close(errorChan) // Close error channel once processing is done

	cpuEnd := measureCPUUsage()
	memEnd := measureMemoryUsage()
	fmt.Printf("Execution Time: %v\nCPU Usage: %.2f%%\nMemory Usage: %d bytes\n",
		time.Since(startTime), cpuEnd-cpuStart, memEnd-memStart)
}

func processFile(file *os.File) {
	r := bufio.NewReader(file)
	var wg sync.WaitGroup

	for {
		lines, err := readLines(r)
		if len(lines) > 0 {
			wg.Add(1)
			go func(lines [][]byte) {
				defer wg.Done()
				for _, line := range lines {
					processLine(line)
				}
			}(lines)
		}
		if err == io.EOF {
			break
		} else if err != nil {
			log.Printf("Error reading file: %v", err)
		}
	}

	wg.Wait()
}

func readLines(r *bufio.Reader) ([][]byte, error) {
	var lines [][]byte
	for i := 0; i < LinesPerWorker; i++ {
		line, err := r.ReadBytes('\n')
		if len(line) > 0 {
			lines = append(lines, append([]byte(nil), line...)) // Copy line to avoid data race
		}
		if err == io.EOF {
			return lines, err
		} else if err != nil {
			return nil, err
		}
	}
	return lines, nil
}

func processLine(line []byte) {
	fields := strings.Split(string(line), ",")
	if missingFields(fields) {
		errorChan <- ErrorLine{
			Line:  string(line),
			Error: fmt.Errorf("missing required fields"),
		}
	}
}

func missingFields(fields []string) bool {
	for pos := range requiredFields {
		if pos >= len(fields) || fields[pos] == "" {
			return true
		}
	}
	return false
}

func handleErrors() {
	errorFile, _ = os.Create("errors.csv")
	defer errorFile.Close()
	errorBuf = bufio.NewWriter(errorFile)
	defer errorBuf.Flush()

	buffer := make([]string, 0, ErrorBatchSize)
	for errLine := range errorChan {
		buffer = append(buffer, fmt.Sprintf("%s, error: %v\n", errLine.Line, errLine.Error))
		if len(buffer) >= ErrorBatchSize {
			flushErrors(buffer)
			buffer = buffer[:0]
		}
	}
	if len(buffer) > 0 {
		flushErrors(buffer)
	}
}

func flushErrors(errors []string) {
	for _, errLine := range errors {
		errorBuf.WriteString(errLine)
	}
	errorBuf.Flush()
}

func measureCPUUsage() float64 {
	return 0.0 // Placeholder for CPU measurement
}

func measureMemoryUsage() uint64 {
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)
	return memStats.Alloc
}
