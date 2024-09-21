import time
import threading
import os
import ctypes

class FileMonitor(threading.Thread):
    def __init__(self, file_paths, check_interval=0.1, callback=None):
        super().__init__()
        self.file_paths = file_paths if isinstance(file_paths, list) else [file_paths]
        self.check_interval = check_interval
        self.last_modified = {path: 0 for path in self.file_paths}
        self.last_size = {path: 0 for path in self.file_paths}
        self.result = []
        self._stop_event = threading.Event()
        self.callback = callback
        print(f"Monitoring files: {self.file_paths}")

    def run(self):
        print(f"Starting FileMonitor thread: {self.name}")
        try:
            while not self._stop_event.is_set():
                for file_path in self.file_paths:
                    try:
                        current_modified = os.path.getmtime(file_path)
                        current_size = os.path.getsize(file_path)
                        
                        if current_modified > self.last_modified[file_path] or current_size > self.last_size[file_path]:
                            print(f"File changed: {file_path}")
                            with open(file_path, 'r') as file:
                                file.seek(self.last_size[file_path])
                                new_content = file.read()
                                if new_content:
                                    print(f"New content in {file_path}: {new_content}")
                                    self.result.append(new_content)
                                    if self.callback:
                                        self.callback(new_content)
                            
                            self.last_modified[file_path] = current_modified
                            self.last_size[file_path] = current_size
                        
                    except Exception as e:
                        print(f"Error monitoring file {file_path}: {e}")
                
                time.sleep(self.check_interval)
        finally:
            print(f"FileMonitor thread {self.name} has exited.")

    def stop(self):
        self._stop_event.set()
        print(f"Stop signal sent to FileMonitor thread {self.name}.")

    def get_latest_result(self, timeout=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.result:
                return self.result.pop(0)
            time.sleep(0.1)
        return None

    def is_alive(self):
        return super().is_alive()

    @staticmethod
    def terminate(thread):
        if thread.is_alive():
            thread_id = thread.ident
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
                print(f'Exception raise failure for thread {thread.name}')
            else:
                print(f'Termination signal sent to thread {thread.name}')

    @classmethod
    def create_and_start(cls, file_paths, check_interval=0.1, callback=None):
        monitor = cls(file_paths, check_interval, callback)
        monitor.start()
        print(f"Started FileMonitor thread: {monitor.name}")
        return monitor

if __name__ == "__main__":
    def example_callback(content):
        print(f"Callback received: {content}")

    # Define two example file paths
    file_path_1 = os.path.join(os.getcwd(), "resources", "2024_09_19_2.log")
    file_path_2 = os.path.join(os.getcwd(), "resources", "2024_09_20_2.log")
    
    print(f"Monitoring files: {file_path_1} and {file_path_2}")
    
    # Create and start a FileMonitor instance with both file paths
    monitor = FileMonitor.create_and_start([file_path_1, file_path_2], callback=example_callback)
    
    TIME_OUT_SECOND = 0.5
    try:
        while True:
            if not monitor.is_alive():
                print("FileMonitor thread is not alive. Restarting...")
                monitor = FileMonitor.create_and_start([file_path_1, file_path_2], callback=example_callback)
                print(f"Current result: {monitor.result}")
            time.sleep(TIME_OUT_SECOND)
    except KeyboardInterrupt:
        print("Stopping monitor...")
        monitor.stop()
        monitor.join(timeout=TIME_OUT_SECOND)
        if monitor.is_alive():
            print(f"FileMonitor thread {monitor.name} couldn't be terminated normally. Forcing termination...")
            FileMonitor.terminate(monitor)
    print(f"Main thread {threading.current_thread().name} exiting.")