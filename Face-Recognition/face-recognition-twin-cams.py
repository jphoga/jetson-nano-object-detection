import face_recognition
import cv2
import numpy as np
import time
import  os
import pickle
from threading import Thread    
print(cv2.__version__)

dispW = 640
dispH = 480
flip = 2
font = cv2.FONT_HERSHEY_SIMPLEX
dtav =  0
fps  = 0

with open('train_pkl', 'rb') as f:
    Names = pickle.load(f)
    Encodings = pickle.load(f)

class vStream:
    def __init__ (self, src, width, height):
        self.width = width
        self.height = height
        self.capture = cv2.VideoCapture(src)
        self.thread = Thread(target = self.update, args = ())
        self.thread.daemon = True
        self.thread.start()
    def update(self):
        while True:
            _,self.frame = self.capture.read()
            self.frame = cv2.resize(self.frame, (self.width, self.height))
    def  getFrame(self):
        return self.frame


camSet='nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'
# cam1 = cv2.VideoCapture(camSet)
# cam2 = cv2.VideoCapture('/dev/video1')
cam1  = vStream('/dev/video2', dispW, dispH)
cam2  = vStream(camSet, dispW, dispH)
startTime  = time.time()
scaleFactor = .25

while True:
    try:
        myFrame1 = cam1.getFrame()
        myFrame2 = cam2.getFrame()
        frameCombined = np.hstack((myFrame1,  myFrame2))
        frameSmall = cv2.resize(frameCombined, (0,0), fx=scaleFactor, fy=scaleFactor)
        frameRGB = cv2.cvtColor(frameSmall, cv2.COLOR_BGR2RGB)
        facePositions = face_recognition.face_locations(frameRGB, model='cnn')
        allEncodings = face_recognition.face_encodings(frameRGB, facePositions)
        for (top, right, bottom,left), face_encoding in zip(facePositions, allEncodings):
            name = 'Unknown Person'
            matches = face_recognition.compare_faces(Encodings, face_encoding)
            if True in matches:
                first_match_index = matches.index(True)
                name = Names[first_match_index]
                print(name)
            top  = int(top/scaleFactor)
            left  = int(left/scaleFactor)
            bottom  = int(bottom/scaleFactor)
            right  = int(right/scaleFactor)
            cv2.rectangle(frameCombined, (left,top),(right,bottom),  (0,0,255), 2)
            cv2.putText(frameCombined, name, (left, top-6),font,.75, (0,0,255), 2)

        dt = time.time() - startTime
        dtav = .9 * dtav + .1 * dt
        fps = 1 / dtav
        startTime =  time.time()
        cv2.rectangle(frameCombined, (0,0),  (130,40),  (0,0,255), -1)
        cv2.putText(frameCombined,  str(round(fps,1)) + ' FPS', (0,25), font, .75, (0,255,255), 2)
        cv2.imshow('Combo', frameCombined)
        cv2.moveWindow('Combo', 0,0)
        
        
    except:
        print('frame not available')
        
    if cv2.waitKey(1) == ord('q'):
        cam1.capture.release()
        cam2.capture.release()
        cv2.destroyAllWindows()
        exit(1)
        break

