import face_recognition
import cv2
import os
import pickle
import time
import threading
from adafruit_servokit import ServoKit
print(cv2.__version__)

dtFIL=0
scanMode  = True
width = 640
height = 480
# Modify for faster FPS (higher number after . => faster but lower accuracy)
scaleFactor = .25
# Modify for faster servo movement (highe number => more stable but slower)
servoScaleFactor = 20
flip = 2
fpsReport = 0

Encodings = []
Names = []

kit=ServoKit(channels=16)
tilt=90
pan=90
dTilt=10
dPan=1
kit.servo[0].angle=pan
kit.servo[1].angle=tilt

print("INFO: Getting training data...")
with  open('train_pkl', 'rb') as f:
    Names = pickle.load(f)
    Encodings = pickle.load(f) 

print("INFO: Setting camera up...")
# piCams  NEW Style
camSet0new='nvarguscamerasrc sensor-id=0 ee-mode=1 ee-strength=0 tnr-mode=2 tnr-strength=1 wbmode=3 ! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1,format=NV12 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(width)+', height='+str(height)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! videobalance contrast=1.3 brightness=-.2 saturation=1.2 ! appsink drop=True'
camSet1new='nvarguscamerasrc sensor-id=1 ee-mode=1 ee-strength=0 tnr-mode=2 tnr-strength=1 wbmode=3 ! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1,format=NV12 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(width)+', height='+str(height)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! videobalance contrast=1.3 brightness=-.2 saturation=1.2 ! appsink drop=True'
# piCams  OLD Style
camSet0old='nvarguscamerasrc sensor-id=0 ! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1,format=NV12 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(width)+', height='+str(height)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink drop=True'
camSet1old='nvarguscamerasrc sensor-id=1 ! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1,format=NV12 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(width)+', height='+str(height)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink drop=True'
# webCam  
camSet2web ='v4l2src device=/dev/video2 ! video/x-raw,width='+str(width)+',height='+str(height)+',framerate=20/1 ! videoconvert ! appsink drop=True'

### OLD ####
# camSet='nvarguscamerasrc !  video/x-raw(memor0y:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'
# cam = cv2.VideoCapture('/dev/video1')
# cam.set(3,640)
# cam.set(4,480)
### OLD ####


cam = cv2.VideoCapture(camSet2web)
font =  cv2.FONT_HERSHEY_SIMPLEX

print("INFO: Start  reading frames...")
timeStamp=time.time()
while True:
    _, frame = cam.read()
    frameSmall = cv2.resize(frame, (0,0), fx=scaleFactor, fy=scaleFactor)
    frameRGB = cv2.cvtColor(frameSmall, cv2.COLOR_BGR2RGB)
    facePositions = face_recognition.face_locations(frameRGB, model='cnn')
    allEncodings = face_recognition.face_encodings(frameRGB, facePositions)
    for (top, right, bottom, left), face_encoding in zip(facePositions, allEncodings):
        name = 'Unknown Person'
        matches = face_recognition.compare_faces(Encodings, face_encoding)
        if True in matches:
            first_match_index = matches.index(True)
            name = Names[first_match_index]
        top = int(top/scaleFactor)
        right = int(right/scaleFactor)
        bottom = int(bottom/scaleFactor)
        left = int(left/scaleFactor)
        cv2.rectangle(frame,(left, top),(right, bottom), (0,0,255), 2)
        cv2.putText(frame, name, (left, top-6),font,.75, (0,0,255), 2)
        scanMode = False
        objX = left + (right - left) / 2
        objY = top + (bottom - top) / 2
        errorPan=objX - width / 2
        errorTilt=objY -height / 2
        if abs(errorPan) > 15:
            pan=pan+errorPan / servoScaleFactor
        if abs(errorTilt) > 15:
            tilt=tilt-errorTilt / servoScaleFactor
        if pan > 180:
            pan = 180
            print("Pan out of range")
        if pan < 0:
            pan = 0
            print("Pan out of range")
        if tilt > 180:
            tilt = 180
            print("Tilt out of range")
        if tilt < 0:
            tilt = 0
            print("Tilt out of range")
        kit.servo[0].angle=pan
        kit.servo[1].angle=tilt
        print(tilt)
        break

    if scanMode == True:
        if pan >= 179:
            dPan = abs(dPan) * (-1)
        if pan <= 1:
            dPan = abs(dPan)
        if pan >=179 or pan <= 1:
            if tilt >= 170:
                dTilt = abs(dTilt) * (-1)
            if tilt <= 10:
                dTilt = abs(dTilt)
            tilt = tilt + dTilt
        pan = pan + dPan
        kit.servo[0].angle=pan
        kit.servo[1].angle=tilt
    scanMode=True
            
    dt = time.time() - timeStamp
    fps = 1 / dt
    fpsReport = .90 * fpsReport + .1 *fps 
    print('FPS: ', round(fpsReport, 1))
    timeStamp =  time.time()
    cv2.rectangle(frame, (0,0),(100,40),(0,0,255), -1)
    cv2.putText(frame, str(round(fpsReport, 1)) + ' fps',(0, 25), font, .75,  (0, 255,255), 2)
    # dt=time.time()-timeMark
    # timeMark=time.time()
    # dtFIL=.9*dtFIL + .1*dt
    # fps=1/dtFIL
    # cv2.rectangle(frame,(0,0),(150,40),(0,0,255),-1)
    # cv2.putText(frame,'fps: '+str(round(fps,1)),(0,30),font,1,(0,255,255),2)
    cv2.imshow('Picture', frame)
    cv2.moveWindow('Picture', 0,0)
    if cv2.waitKey(1) == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()
