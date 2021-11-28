from typing import NewType
import cv2
import time
import os, sys
import numpy as np
from threading import Thread
from datetime import datetime
from camera import VideoCapture
from flask import Flask, Response, render_template, jsonify, request, redirect, flash, url_for
from waitress import serve



global screenshot, grey, switch, negative, rec, rec_frame, out
screenshot=0
grey=0
switch=1
negative=0
rec=0


## Declaring flask app 
app = Flask(__name__)

## Import camera method from camera class, import camera object
video_stream = VideoCapture()
camera = video_stream.self()

#camera = cv2.VideoCapture(0)



# def gen1():
#     global out, screenshot, rec_frame
#     while True:
#         #frame = camera.get_frame()
#         success, frame = camera.read()

#         if success:
#             if(grey):
#                 frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             if(negative):
#                 frame = cv2.bitwise_not(frame)
#             if(screenshot):
#                 screenshot=0
#                 now = datetime.now()
#                 path = os.path.sep.join(['screenshots', "screenshot_{}.png".format(str(now).replace(":",''))])
#                 cv2.imwrite(path, frame)
#             if(rec):
#                 rec_frame=frame
#                 frame = cv2.putText(cv2.flip(frame, 1), "Recording Stream..", (0,25), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 4)
#                 frame = cv2.flip(frame, 1)
#             try:
#                 ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
#                 frame = buffer.tobytes()
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
#             except Exception as e:
#                 pass
#         else: 
#             pass

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)

        

def gen2(camera):
    global out, screenshot, rec_frame
    while True:
        #frame = camera.get_frame()
        success, frame = camera.read()

        if(success):
            if(grey):
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if(negative):
                frame = cv2.bitwise_not(frame)
            if(screenshot):
                screenshot=0
                now = datetime.now()
                path = os.path.sep.join(['screenshots', "screenshot_{}.png".format(str(now).replace(":",''))])
                cv2.imwrite(path, frame)
            if(rec):
                rec_frame=frame
                frame = cv2.putText(cv2.flip(frame, 1), "Recording Stream..", (0,25), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 4)
                frame = cv2.flip(frame, 1)
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            except Exception as e:
                pass
            else: 
                pass


        # yield (b'--frame\r\n'
        #        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


############### Routes ##################
@app.route("/")
def index():
    return render_template('index.html')


@app.route("/live")
def live():
    return render_template('live.html')


@app.route("/video_feed")
def video_feed():
    return Response(gen2(video_stream), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/filters", methods=['POST', 'GET'])
def filters():
    global switch, camera
    if request.method == 'POST':
        ##Take screenshot of stream
        if request.form.get('screenshot') == 'Screenshot':
            global screenshot
            screenshot = 1
        ##Apply greyscale filter
        elif request.form.get('grey') == 'Grey':
            global grey
            grey = 1
        ##Apply Negative Filter
        elif request.form.get('negative') == 'Negative':
            global negative
            negative = 1
        ##Start/ Stop livestream
        elif request.form.get('stop') == 'Stop/Start':
            if(switch == 1):
                switch = 0
                video_stream.__del__()
                cv2.destroyAllWindows
            else:
                camera = video_stream.__init__()
                switch = 1

        ##record video, output not working, corrupted file.
        elif request.form.get('rec') == 'Start/Stop Recording':
            global rec, out 
            rec = not rec
            if(rec):
                now = datetime.now()
                save = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('vid_{}.avi'.format(str(now).replace(":",'')), save, 20.0, (640, 480))
                thread = Thread(target = record, args=[out,])
                thread.start
            elif(rec==False):
                out.release()

    elif request.method=='GET':
        return render_template('live.html')
    return render_template('live.html')



################# Host Params ####################
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False,port="5000")
    #serve(app, host='0.0.0.0', port=5000)

camera.release()
cv2.destroyAllWindows()