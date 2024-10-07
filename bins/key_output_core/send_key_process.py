import multiprocessing
import win32gui
import win32con
import win32api
import time

class SendKeyProcess(multiprocessing.Process):
    def __init__(self, hwnd, text):
        super().__init__()
        self.hwnd = hwnd
        self.text = text

    def run(self):
        for char in self.text:
            win32api.SendMessage(self.hwnd, win32con.WM_CHAR, ord(char), 0)
            time.sleep(0.02)

def send_keys_background(hwnd, text):
    process = SendKeyProcess(hwnd, text)
    process.start()
    return process