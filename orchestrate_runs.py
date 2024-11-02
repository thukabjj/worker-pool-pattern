import subprocess
import sys
import os

def delete_existing_results():
    """Delete existing result and summary CSV files."""
    files_to_delete = [
        "java_results.csv", "java_summary.csv",
        "go_results.csv", "go_summary.csv"
    ]
    for file in files_to_delete:
        if os.path.exists(file):
            os.remove(file)
            print(f"Deleted existing file: {file}")

def run_script(script_name):
    """Helper function to run a given Python script."""
    try:
        print(f"Running {script_name}...")
        subprocess.run(["python3", script_name], check=True)
        print(f"{script_name} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")
        sys.exit(1)

def main():
    # Paths to each benchmark script
    java_script = "run_java.py"
    go_script = "run_go.py"

    # Ensure both scripts exist
    if not os.path.exists(java_script):
        print(f"Error: {java_script} not found.")
        sys.exit(1)
    if not os.path.exists(go_script):
        print(f"Error: {go_script} not found.")
        sys.exit(1)

    # Delete any existing results files
    delete_existing_results()

    # Run Java benchmark script (using native image)
    run_script(java_script)

    # Run Go benchmark script
    run_script(go_script)

    print("Both benchmarks completed successfully. Results are saved to 'java_results.csv', 'java_summary.csv', 'go_results.csv', and 'go_summary.csv'.")

    # Optional: Launch analysis script if desired
    analyze_script = "analyze_results.py"
    if os.path.exists(analyze_script):
        run_analysis = input("Would you like to run analysis on the results? (y/n): ").strip().lower()
        if run_analysis == 'y':
            run_script(analyze_script)
        else:
            print("Skipping analysis.")
    else:
        print("Analysis script not found. Skipping analysis.")

if __name__ == "__main__":
    main()
