## Run this script in another terminal.
## The sample_call() of the output_simulate.py should output commands to this terminal.
## You must press Enter to what this script received in time that depends on the sample_call() waiting time.

from datetime import datetime
import os
import re

def append_text_to_log(input_command):
    # Search for the input_command in command_sample.txt
    with open('resources/command_sample.txt', 'r') as sample_file:
        sample_content = sample_file.read()
        pattern = r'>(.*?{}.*?)(?=>|\Z)'.format(re.escape(input_command))
        match = re.search(pattern, sample_content, re.DOTALL)

    if match:
        captured_content = match.group(1).strip()
    else:
        captured_content = "Command not found"

    # Get the current date and time
    current_time = datetime.now().strftime('%Y %B %d, %A, %H:%M:%S')

    # Prepare the log entry
    log_entry = f"{current_time}\n{captured_content}\n\n"

    # Append the log entry to the specified file
    with open(os.path.join(os.getcwd(), 'resources', 'test.log'), 'a') as log_file:
        log_file.write(log_entry)

if __name__ == "__main__":
    try:
        while True:
            input_command = input("Enter the command to search for: ")
            append_text_to_log(input_command)
            print("Command processed. Enter another command or press Ctrl+C to exit.")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")

