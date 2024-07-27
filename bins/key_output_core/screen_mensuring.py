import numpy as np
from PIL import ImageGrab
import threading
import time
import cv2

class ScreenCapture(threading.Thread):
    def __init__(self, mse_threshold:float = 3.0):
        super().__init__()
        self.mismatch = 0
        self.__basic_img = None
        self.__threshold = mse_threshold
        self.__flag = threading.Event()
        self.__flag.set()
    
    def __capture(self):
        return cv2.cvtColor(np.array(ImageGrab.grab()),cv2.COLOR_BGR2GRAY)
    
    def Get1stImage(self):
        self.__basic_img = self.__capture()

    def mse(self,img1,img2):
        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;
        # Note: the two images must have the same dimension
        err = np.sum((img1.astype("float")-img2.astype("float"))**2)
        err /= float(img1.shape[0]*img1.shape[1])
        return err # return the MSE, the lower the error, the more "similar"
    
    def run(self):
        while self.__flag.is_set():
            img2 = self.__capture()
            print(f'{threading.current_thread().name} get 2nd img.')
            mse_diff = self.mse(self.__basic_img,img2)
            self.mismatch = mse_diff
            if mse_diff>=self.__threshold:
                print('clear')
                self.__flag.clear()
            time.sleep(0.1)
########################################################################################



def sample_call():
    screen_capture = ScreenCapture()
    input("Enter what you like to say:\n")
    screen_capture.Get1stImage()
    screen_capture.start()
    start = time.time()
    while screen_capture.is_alive():
       time.sleep(0.3)
       running_time = time.time() - start
       print(f"{running_time:.2f}")
       if running_time > 10:
           screen_capture.join()
           break
       print(f"{threading.current_thread().name} got the diff {screen_capture.mismatch:.2f}.")

if __name__ == "__main__":
    sample_call()
