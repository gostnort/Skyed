from pynput.keyboard import Controller, Key
from pynput.mouse import Listener as mouse_listener
import time
import threading
import concurrent.futures
import yaml
import sys
import os

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
            print(f'Thread {threading.current_thread().name} stopped.')

class SendKey(threading.Thread):
    def __init__(self,F12Pending=5,OperatePending=0.1):
        super().__init__()
        self.__keyboard = Controller()
        self.__op_delay = OperatePending
        self.__str_delay = F12Pending
        self.__flag = threading.Event()
        self.__flag.set()
        self.__lock=threading.Lock()

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
    def execute_command(self,OutputText:str,F12PendingFunc:None,bClear=True,bEsc=True,bF12=True,bPrint=True):
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
                    end_time = start_time
                    future = executor.submit(F12PendingFunc) # A new thread for another function to mensure the time.
                    while True:
                        end_time=time.time()                      
                        if future.done():
                            print(f"{threading.current_thread().name} ends the F12_While due to reaching foreign pending time.")
                            break
                        if end_time-start_time > self.__str_delay:
                            print(f"{threading.current_thread().name} ends the F12_While due to reaching max delay time.")
                            break
                        time.sleep(0.05)
                else:
                    time.sleep(self.__op_delay)
######################################################################



def sample_call():
    import timeit
    send_key=SendKey()
    list_str=['sy ca983/26jul/pek','pf1']
    list_index = 0
    mouse=MouseClickMonitor(3)
    mouse.start()
    file_path = get_file_path_from_config()
    print(f"Monitoring file: {file_path}")
    monitor = FileMonitor(file_path)
    monitor.start()
    while mouse.is_alive(): # the main thread is not waiting without this while loop.
        if mouse.count > 0:
            if list_index != len(list_str):
                total_time=timeit.timeit(lambda: send_key.execute_command(list_str[list_index], monitor.get_latest_result, bPrint=False),
                                         number=1)
                print(f"Index {list_index} consumes time {total_time:.4f} second.")
                result = monitor.get_latest_result(timeout=5)  # Get the result from the monitoring module
                if result:
                    print(f"Latest result: {result}")
                else:
                    print("No new content detected")
                list_index = list_index + 1
        if mouse.count == 3:
            print("Stopping monitor...")
            monitor.stop()
            mouse.stop()
            break
        time.sleep(0.3)# avoid this While consume too much CPU.

def get_file_path_from_config():
    with open('resources/keyboard_outputing.yml', 'r') as file:
        config = yaml.safe_load(file)
    return config['default_path']

if __name__=="__main__":
    sample_call()