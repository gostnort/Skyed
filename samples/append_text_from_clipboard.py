import pyperclip
from datetime import datetime
import os

def append_clipboard_to_log(file_path):
    # Get the current clipboard content
    clipboard_content = pyperclip.paste()

    # Get the current date and time
    current_time = datetime.now().strftime('%Y %B %d, %A, %H:%M:%S')

    # Prepare the log entry
    log_entry = f"{current_time}\n{clipboard_content}\n\n"

    # Append the log entry to the specified file
    with open(file_path, 'a') as log_file:
        log_file.write(log_entry)

if __name__ == "__main__":
    file_path = os.path.join(os.getcwd(),'resources','test.log')
    append_clipboard_to_log(file_path)
