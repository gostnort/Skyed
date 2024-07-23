import os
import time
def ReadTxt2String(txt_file_path)->str:
    max_attempts = 10  # Maximum number of attempts
    attempts = 0
    while attempts < max_attempts:
        try:
            with open(txt_file_path, 'rt') as txtObj:
                txtContent = txtObj.read()
            return txtContent
        except IOError:  # This catches file access issues
            attempts += 1
            if attempts < max_attempts:
                time.sleep(0.2)  # Wait for 2 seconds before retrying
            else:
                raise IOError(f"Failed to open {txt_file_path} after {max_attempts} attempts")
    return ""

def ReadTxt2List(txt_file_path)->list:
    max_attempts = 10  # Maximum number of attempts
    attempts = 0
    while attempts < max_attempts:
        try:
            with open(txt_file_path, 'rt') as txtObj:
                txtContent = txtObj.readlines()
            return txtContent
        except FileNotFoundError:
            print(f"Error: File '{txt_file_path}' not found.")
            return []
        except IOError:  # This catches other file access issues
            attempts += 1
            if attempts < max_attempts:
                time.sleep(0.2)  # Wait for 2 seconds before retrying
            else:
                print(f"Error: Failed to open '{txt_file_path}' after {max_attempts} attempts.")
                return []

    # This line should never be reached, but it's here for completeness
    return []
    
def String2List(MultilineString):
    # Use splitlines() to split the string into a list of lines
    return MultilineString.splitlines()

def List2String(Lines):
    return '\n'.join(Lines)

def AppendText(TxtPath,Text):
    end_time = time.time() + 1  # 1 second from now
    while time.time() < end_time:
        if os.access(TxtPath, os.W_OK):
            try:
                with open(TxtPath, 'a') as file:
                    file.write(Text + '\n')
                    break
            except IOError as e:
                print(f"Error writing to file: {e}. Retrying in 100ms...")
        else:
            print(f"{TxtPath} file is locked by another program, retrying in 100ms...")
        time.sleep(0.1)  # sleep for 100ms
    else:
        print("Could not write to file after 1 second.")

def main():
    AppendText(r'C:\Users\gostn\my_github\pdstar0.2\resources\qqqqq.txt','A')

if __name__ == '__main__':
    main()