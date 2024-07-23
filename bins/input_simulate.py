from pynput.keyboard import Controller, Key
from pynput.mouse import Listener as mouse_listener
import time
import threading
import concurrent.futures

class MouseClickMonitor(threading.Thread):
    def __init__(self, ExitClickCount=1):
        super().__init__()
        self.__timer = threading.Timer(0.3, self.__start_listener)
        self.__listener = None
        self.bRunning=True
        self.__exit = ExitClickCount
        self.__count = 0
        self.__lock = threading.Lock()
        self.__flag = threading.Event()
        self.__flag.set()
    
    def __on_click(self, x, y, button, pressed):
        if pressed:
            with self.__lock:
                self.__count += 1
                if self.__count >= self.__exit:
                    self.stop()
                    print(f'Thread {threading.current_thread().name} changes bRunning to False')
                    self.bRunning=False
                    return False

    def __start_listener(self):
        self.__listener = mouse_listener(on_click=self.__on_click)
        with self.__listener as listener:
            listener.join()

    def run(self):
        # Start the timer
        print(f"{threading.current_thread().name} started. Will monitor mouse after 500ms delay.")
        self.__timer.start()
        # Wait for the timer to finish to avoid interpreter shutdown issues
        self.__timer.join()
        print(f"{threading.current_thread().name} joined.")
        self.__flag.wait()
    
    def stop(self):
        if self.__listener:
            self.__listener.stop()

    def pause(self):
        self.__flag.clear() # block the thread.

    def resume(self):
        self.__flag.set() # unblock the thread.


class SendKey(threading.Thread):
    def __init__(self,delay=0.5):
        super().__init__()
        self.__keyboard = Controller()
        self.__delay = delay
        self.__lock=threading.Lock()
        self.__flag = threading.Event() # Event to be paused as a flag.
        self.__flag.set() # Set the flag to True.
        self.bRunning = True

    def __type_keys(self, keys):
        time.sleep(self.__delay)  # Delay between each task
        with self.__lock:
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
        
    def __pause(self):
        self.__flag.clear() # block the thread.

    def __resume(self):
        self.__flag.set() # unblock the thread.

    def stop(self):
        self.bRunning = False # stop the thread.

    def is_active(self):
        return self.bRunning

    def __type_string(self, string):
        for char in string:
            self.__keyboard.press(char)
            self.__keyboard.release(char)
            self.__pause()
            time.sleep(0.05)
            self.__resume()
    
    def execute_command(self,Keys,bClear=True,bEsc=True,bF12=True,bPrint=True):
        key_combinations = []
        if bClear:
            key_combinations.append([Key.ctrl, 'a']) 
        if bEsc:
            key_combinations.append(Key.esc)
        key_combinations.append(Keys)
        if bF12:
            key_combinations.append(Key.f12)
        if bPrint:
            key_combinations.append([Key.ctrl, 'p'])
        print(key_combinations)
        with concurrent.futures.ThreadPoolExecutor() as executor: # Call .start() automatically..
            while self.bRunning:
                self.__flag.wait()
                time.sleep(self.__delay)
                for key in key_combinations:
                    executor.submit(self.__type_keys, key)
                    self.__pause()
                    time.sleep(self.__delay)
                    self.__resume()
# =========================================================

def sample_call_MouseClickMonitor():
    mouse=MouseClickMonitor()# Thread_1
    mouse1=MouseClickMonitor(2)# Thread_2
    mouse.run() # Thread_1 starts.
    send_key=SendKey(0.5) # Thread_3
    list_keys=['w/o a','hello world']
    list_index=0
    start=time.time()
    mouse.stop() # Thread_1 stops.
    mouse1.start() # Thread_2 starts. Inherited the 1st click. Don't know why.
    while mouse1.bRunning: # If the Thread_2 is allowed running:
        send_key.execute_command(list_keys[list_index])
        list_index+=1
        if list_index>=len(list_keys):
            break # Thread_3 would stop.
        if time.time()-start>10:
            break
    mouse1.stop() # Thread_2 stops.

def sample_send_keys():
    send_keys = SendKey(0.5)
    send_keys.execute_command('w/o a',bPrint=False)   
    send_keys.execute_command('hello world') 
if __name__=="__main__":
    sample_call_MouseClickMonitor()