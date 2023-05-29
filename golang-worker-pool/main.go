package main

import (
	"bufio"
	"fmt"
	"io"
	"log"
	"math"
	"os"
	"os/exec"
	"runtime"
	"strings"
	"sync"
	"time"
)

// Number of lines each worker will process
const LinesPerWorker = 1000

// Required fields are identified by their position in the CSV line
var requiredFields = map[int]bool{
	0: true, // id
	3: true, // email
}

// ErrorLine represents a line that could not be processed
type ErrorLine struct {
	Line  string
	Error error
}

var (
	mu        sync.Mutex
	errorFile *os.File
	bw        *bufio.Writer
)

func main() {

	const fileName = "./data_100000.csv"

	file, err := os.Open(fileName)

	if err != nil {
		log.Fatalf("cannot able to read the file: %v", err)
	}

	defer file.Close()

	errorLines := make(chan ErrorLine)

	go Process(file, errorLines)

	cpuStart := measureCPUUsage()
	memStart := measureMemoryUsage()

	startTime := time.Now()

	for errLine := range errorLines {
		mu.Lock()
		if errorFile == nil {
			var err error
			errorFile, err = os.Create("errors.csv")
			if err != nil {
				log.Fatalf("Failed to create error file: %v", err)
			}
			bw = bufio.NewWriter(errorFile)
		}
		_, err := bw.WriteString(fmt.Sprintf("%s, error: %s\n", errLine.Line, errLine.Error))
		if err != nil {
			log.Fatalf("Failed to write to error file: %v", err)
		}
		mu.Unlock()
	}

	if bw != nil {
		if err := bw.Flush(); err != nil {
			log.Fatalf("Failed to flush error file: %v", err)
		}
	}
	if errorFile != nil {
		if err := errorFile.Close(); err != nil {
			log.Fatalf("Failed to close error file: %v", err)
		}
	}

	cpuEnd := measureCPUUsage()
	memEnd := measureMemoryUsage()
	totalMemUsage := (memEnd - memStart)

	endTime := time.Now()
	executionTime := endTime.Sub(startTime)

	fmt.Println("Execution Time:", executionTime)
	fmt.Println("CPU Usage:", cpuEnd-cpuStart, "%")
	fmt.Println("Memory Usage Begin:", memStart, "bytes")
	fmt.Println("Memory Usage End:", memEnd, "bytes")
	fmt.Println("Memory Usage:", totalMemUsage, "bytes")
}

func Process(f *os.File, errorLines chan<- ErrorLine) {

	linesPool := sync.Pool{
		New: func() interface{} {
			lines := make([]byte, LinesPerWorker)
			return lines
		},
	}

	stringPool := sync.Pool{
		New: func() interface{} {
			lines := ""
			return lines
		},
	}

	r := bufio.NewReader(f)

	var wg sync.WaitGroup

	for {
		buf := linesPool.Get().([]byte)

		n, err := r.Read(buf)
		buf = buf[:n]

		if n == 0 {
			if err != nil && err != io.EOF {
				log.Printf("Error reading file: %v", err)
			}
			break
		}

		nextUntillNewline, err := r.ReadBytes('\n')

		if err != io.EOF {
			buf = append(buf, nextUntillNewline...)
		}

		wg.Add(1)
		go func() {
			ProcessChunk(buf, &linesPool, &stringPool, errorLines)
			wg.Done()
		}()

	}
	wg.Wait()
	close(errorLines)
}

func ProcessChunk(chunk []byte, linesPool *sync.Pool, stringPool *sync.Pool, errorLines chan<- ErrorLine) {

	var wg2 sync.WaitGroup

	entries := stringPool.Get().(string)
	entries = string(chunk)

	linesPool.Put(chunk)

	entriesSlice := strings.Split(entries, "\n")

	stringPool.Put(entries)

	chunkSize := 300
	n := len(entriesSlice)
	noOfThread := n / chunkSize

	if n%chunkSize != 0 {
		noOfThread++
	}

	for i := 0; i < noOfThread; i++ {
		wg2.Add(1)
		go func(start int, end int) {
			defer wg2.Done()
			for i := start; i < end; i++ {
				text := entriesSlice[i]
				if len(text) == 0 {
					continue
				}
				entry := strings.Split(text, ",")

				// Check for required fields
				for fieldPos, required := range requiredFields {
					if required && (len(entry) <= fieldPos || entry[fieldPos] == "") {
						errorLines <- ErrorLine{
							Line:  text,
							Error: fmt.Errorf("missing required field at position %d", fieldPos),
						}
						break
					}
				}
			}
		}(i*chunkSize, int(math.Min(float64((i+1)*chunkSize), float64(len(entriesSlice)))))
	}

	wg2.Wait()
}

func measureCPUUsage() float64 {
	cmd := exec.Command("sh", "-c", "ps -o %cpu= -p $$")
	output, err := cmd.Output()
	if err != nil {
		log.Fatalf("Failed to measure CPU usage: %v", err)
	}
	cpuUsageStr := strings.TrimSpace(string(output))
	var cpuUsage float64
	_, err = fmt.Sscanf(cpuUsageStr, "%f", &cpuUsage)
	if err != nil {
		log.Fatalf("Failed to parse CPU usage: %v", err)
	}
	return cpuUsage
}

func measureMemoryUsage() uint64 {
	memStart := runtime.MemStats{}
	runtime.ReadMemStats(&memStart)
	return memStart.Alloc
}
