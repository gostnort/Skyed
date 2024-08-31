import time
import threading
import os

class FileMonitor(threading.Thread):
    def __init__(self, file_path, check_interval=0.1):
        super().__init__()
        self.file_path = file_path
        self.check_interval = check_interval
        self.last_modified = 0
        self.last_size = 0
        self.result = []
        self._stop_event = threading.Event()
        print(f"Monitoring file: {self.file_path}")

    def run(self):
        while not self._stop_event.is_set():
            try:
                current_modified = os.path.getmtime(self.file_path)
                current_size = os.path.getsize(self.file_path)
                
                if current_modified > self.last_modified or current_size > self.last_size:
                    print(f"File changed: {self.file_path}")
                    with open(self.file_path, 'r') as file:
                        file.seek(self.last_size)
                        new_content = file.read()
                        if new_content:
                            print(f"New content: {new_content}")
                            self.result.append(new_content)
                    
                    self.last_modified = current_modified
                    self.last_size = current_size
                
            except Exception as e:
                print(f"Error monitoring file: {e}")
            
            time.sleep(self.check_interval)

    def stop(self):
        self._stop_event.set()

    def get_latest_result(self, timeout=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.result:
                return self.result.pop(0)
            time.sleep(0.1)
        return None

if __name__ == "__main__":
    file_path = os.path.join(os.getcwd(), "resources", "test.log")
    print(f"Monitoring file: {file_path}")
    monitor = FileMonitor(file_path)
    monitor.start()
    try:
        while True:
            result = monitor.get_latest_result()
            if result:
                print(f"Latest result: {result}")
            else:
                print("No new content")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping monitor...")
        monitor.stop()
        monitor.join()