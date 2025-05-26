import sys

log_file_path = "tick_execution.log"
print(f"Attempting to write to: {log_file_path}") # This will go to stdout

try:
    with open(log_file_path, "w") as log_file:
        log_file.write("Test log entry.\n")
        log_file.flush()
    print(f"Successfully wrote to: {log_file_path}")
except Exception as e:
    print(f"Error writing to log file: {e}")

sys.exit(0)
