import os
import cv2
import time



class VideoCapture(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()       

    def self(self):
        return self.video

    def read(self):
        frame = self.video.read()
        return frame

    def get_frame(self):
        ret, frame = self.video.read()
    
        ret, jpeg = cv2.imencode('.jpg', frame)

        return jpeg.tobytes()

cv2.destroyAllWindows
