from pynput.keyboard import Controller, Key
from pynput.mouse import Listener as mouse_listener
import time
import threading
import concurrent.futures
import yaml
import sys
import os
import ctypes
import re
from datetime import datetime, timedelta

# Add the bins directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from bins.key_output_core.file_monitor import FileMonitor  # Import the FileMonitor class

class MouseClickMonitor(threading.Thread):
    def __init__(self, ExitClickCount=1):
        super().__init__()
        self.__listener = mouse_listener(on_click=self.__on_click)
        self.__exit = ExitClickCount
        self.count = 0
        self.__lock = threading.Lock()
    
    def run(self):
        print(f"Starting MouseClickMonitor thread: {self.name}")
        with self.__listener as listener:
            listener.join()

    def __on_click(self, x, y, button, pressed):
        if pressed:
            with self.__lock:
                self.count += 1
                print(f"Mouse clicked {self.count} times.")
                if self.count >= self.__exit:
                    self.stop()
                    return False

    def stop(self):
        if self.__listener:
            self.__listener.stop()
            print(f'MouseClickMonitor thread {self.name} stopped.')

class SendKey(threading.Thread):
    def __init__(self, F12Pending=5, OperatePending=0.1):
        super().__init__()
        print(f"Starting SendKey thread: {self.name}")
        self.__keyboard = Controller()
        self.__op_delay = OperatePending
        self.__str_delay = F12Pending
        self.__flag = threading.Event()
        self.__flag.set()
        self.__lock = threading.Lock()

    def __type_keys(self, keys):
        print(f"{threading.current_thread().name} is sending {keys}.")
        with self.__lock: # Ensure the other threads won't be executed before this function is over.
            if isinstance(keys, str):  # Handle string.
                self.__type_string(keys)
                return
            if isinstance(keys, list):  # Handle key combinations
                for key in keys:
                    self.__keyboard.press(key)
                for key in reversed(keys):
                    self.__keyboard.release(key)
            else:
                self.__keyboard.press(keys)
                self.__keyboard.release(keys)

    def __type_string(self, string):
        for char in string:
            self.__keyboard.press(char)
            self.__keyboard.release(char)
            time.sleep(0.02)

    def __pause(self):
        self.__flag.clear() # block the thread.

    def __resume(self):
        self.__flag.set() # unblock the thread.

    # F12PendingFunc must be the ScreenCapture() class including Get1stImage() and start().
    def execute_command(self, OutputText:str, F12PendingFunc:None, bClear=True, bEsc=True, bF12=True, bPrint=True):
        key_combinations = []
        if bClear:
            key_combinations.append([Key.ctrl, 'a']) 
        if bEsc:
            key_combinations.append(Key.esc)
        key_combinations.append(OutputText)
        if bF12:
            key_combinations.append(Key.f12)
        if bPrint:
            key_combinations.append([Key.ctrl, 'p'])
        with concurrent.futures.ThreadPoolExecutor() as executor: # Call .start() automatically..
            for key in key_combinations:
                executor.submit(self.__type_keys, key)
                if key == Key.f12: # From now on, the main thread will running the rest, excpet `future`.
                    print('F12 is pressed.')
                    start_time = time.time()
                    future = executor.submit(F12PendingFunc) # A new thread for another function to mensure the time.
                    while True:
                        if future.done():
                            print(f"{threading.current_thread().name} ends the F12_While due to reaching foreign pending time.")
                            break
                        if time.time() - start_time > self.__str_delay:
                            print(f"{threading.current_thread().name} ends the F12_While due to reaching max delay time.")
                            break
                        time.sleep(0.05)
                    # Wait for the result from F12PendingFunc
                    result = future.result()
                    if result is None:
                        print("No result received from F12PendingFunc")
                else:
                    time.sleep(self.__op_delay)
            print(f"SendKey thread {self.name} finished executing command.")

    def stop(self):
        self.__flag.clear()
        print(f'SendKey thread {self.name} stopped.')

def is_thread_alive(thread):
    return thread.is_alive() if thread else False

def terminate_thread(thread):
    if thread and thread.is_alive():
        thread_id = thread.ident
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

def sample_call():
    send_key = SendKey()
    list_str = ['SE:CA818/01JUN24/*IADLAX', 'PD: CA818/01JUN24*LAX,INAD']
    list_index = 0
    STOP_LISTEN_MOUSE = 2
    TIME_OUT_SECOND = 1
    mouse = MouseClickMonitor(STOP_LISTEN_MOUSE)
    mouse.start()
    print(f"Started MouseClickMonitor thread: {mouse.name}")
    file_path = get_file_path_from_config()
    print(f"Monitoring file: {file_path}")
    monitor = FileMonitor.create_and_start(file_path, callback=file_change_callback)
    time.sleep(0.1)  # Give some time for the thread to start
    try:
        while mouse.is_alive() and monitor.is_alive():
            if mouse.count > 0:
                if list_index < len(list_str):
                    # Add a small delay to ensure the FileMonitor thread is ready
                    time.sleep(0.1)
                    send_key.execute_command(list_str[list_index], monitor.get_latest_result, bPrint=False)
                    result = monitor.get_latest_result(timeout=TIME_OUT_SECOND)
                    if result:
                        print(f"Latest result: {result}")
                    else:
                        print("No new content detected")
                    list_index += 1
                else:
                    print("All commands executed. Exiting...")
                    break  # Exit the while loop after completing all commands
            if mouse.count == STOP_LISTEN_MOUSE:
                print("Mouse click limit reached. Exiting...")
                break
            time.sleep(0.3)  # avoid this While consume too much CPU.
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cleanup_threads(monitor, mouse, TIME_OUT_SECOND)

def get_file_path_from_config():
    with open('resources/processing.yml', 'r') as file:
        config = yaml.safe_load(file)
    
    default_log_folder = config['default_log_folder']
    default_log_name_re = config['default_log_name_re']
    
    return find_latest_log_file(default_log_folder, default_log_name_re)

def find_latest_log_file(folder_path, file_name_pattern):
    today = datetime.now()
    
    for _ in range(2):  # Try today and yesterday
        date_str = today.strftime('%Y_%m_%d')
        files = [f for f in os.listdir(folder_path) if f.startswith(date_str) and re.match(file_name_pattern, f)]
        
        if files:
            # Sort files by modification time (newest first)
            files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
            return os.path.join(folder_path, files[0])
        
        today -= timedelta(days=1)  # Try yesterday's date
    
    return None  # If no file is found

def file_change_callback(content):
    print(f"File changed. New content: {content}")

def cleanup_threads(monitor, mouse, timeout=1):
    print("The finally is cleaning up threads...")
    monitor.stop()
    mouse.stop()
    # Ensure threads are terminated
    terminate_thread(monitor)
    terminate_thread(mouse)
    monitor.join(timeout=timeout)
    mouse.join(timeout=timeout)
    if monitor.is_alive():
        print(f"FileMonitor thread {monitor.name} couldn't be terminated normally. Forcing termination...")
        FileMonitor.terminate(monitor)
    else:
        print(f"FileMonitor thread {monitor.name} terminated.")
    if mouse.is_alive():
        print(f"MouseClickMonitor thread {mouse.name} couldn't be terminated normally.")
    else:
        print(f"MouseClickMonitor thread {mouse.name} terminated.")
    print(f"Main thread {threading.current_thread().name} exiting.")

if __name__=="__main__":
    file_path = get_file_path_from_config()
    if file_path:
        print(f"Latest log file found: {file_path}")
        sample_call()
    else:
        error_message = "No suitable log file found for today or yesterday."
        print(error_message)
        # Here you would typically update the text_area in the briefing_ui
        # For example: update_briefing_ui_text_area(error_message)