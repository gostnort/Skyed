import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_path, event, result):
        self.file_path = file_path
        self.last_size = 0
        self.event = event
        self.result = result

    def on_modified(self, event):
        if event.src_path == self.file_path:
            with open(self.file_path, 'r') as file:
                file.seek(self.last_size)
                new_content = file.read()
                self.last_size = file.tell()
                if new_content:
                    self.result.append(new_content)
                    self.event.set()  # Signal that new content is available

class FileMonitor(threading.Thread):
    def __init__(self, file_path, check_interval=1):
        super().__init__()
        self.file_path = file_path
        self.check_interval = check_interval
        self.observer = Observer()
        self.event = threading.Event()
        self.result = []
        self.handler = FileChangeHandler(file_path, self.event, self.result)

    def run(self):
        self.observer.schedule(self.handler, path=self.file_path, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    def stop(self):
        self.observer.stop()

    def get_latest_result(self, timeout=None):
        if self.event.wait(timeout):  # Wait for the event to be set with a timeout
            self.event.clear()  # Clear the event for the next use
            if self.result:
                return self.result.pop(0)  # Return the latest result
        return None  # Return None if timeout occurs

if __name__ == "__main__":
    file_path = "path/to/your/file.txt"  # Replace with your file path
    monitor = FileMonitor(file_path)
    monitor.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()