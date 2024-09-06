## Run this script in another terminal.
## The sample_call() of the output_simulate.py should output commands to this terminal.
## You must press Enter to what this script received in time that depends on the sample_call() waiting time.

from datetime import datetime
import os
import re

def append_text_to_log(input_command):
    parent_folder = os.path.dirname(os.getcwd())
    with open(os.path.join(parent_folder, 'resources', 'samples','command_sample.txt'), 'r') as sample_file:
        sample_content = sample_file.read()
        # Find the input_command first
        command_index = sample_content.find(input_command)
        
        if command_index != -1:
            # Find the previous ">" before the command, or set to 0 if not found
            start_index = sample_content.rfind('>', 0, command_index)
            start_index = start_index + 1 if start_index != -1 else 0
            
            # Find the next ">" after the command or set to end of file if not found
            end_index = sample_content.find('>', command_index)
            end_index = end_index if end_index != -1 else len(sample_content)
            
            captured_content = sample_content[start_index:end_index].strip()
        else:
            captured_content = "Command not found"

    # Get the current date and time
    current_time = datetime.now().strftime('%Y %B %d, %A, %H:%M:%S')

    # Prepare the log entry
    log_entry = f"{current_time}\n{captured_content}\n\n"

    # Append the log entry to the specified file
    with open(os.path.join(parent_folder, 'resources', 'test.log'), 'a') as log_file:
        log_file.write(log_entry)

if __name__ == "__main__":
    try:
        while True:
            input_command = input("Enter the command to search for: ")
            append_text_to_log(input_command)
            print("Command processed. Enter another command or press Ctrl+C to exit.")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")

