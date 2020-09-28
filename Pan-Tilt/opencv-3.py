import numpy as np
import cv2
import time
from adafruit_servokit import ServoKit
print(cv2.__version__)

kit=ServoKit(channels=16)
tilt=90
pan=90
dPan=1
dTilt=10

kit.servo[0].angle=pan
kit.servo[1].angle=tilt

timeMark = time.time()
dtFIL=0
width=640
height=480
flip=2
font=cv2.FONT_HERSHEY_SIMPLEX

# piCams  NEW Style
camSet1='nvarguscamerasrc sensor-id=0 ee-mode=1 ee-strength=0 tnr-mode=2 tnr-strength=1 wbmode=3 ! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1,format=NV12 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(width)+', height='+str(height)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! videobalance contrast=1.3 brightness=-.2 saturation=1.2 ! appsink drop=True'
camSet11='nvarguscamerasrc sensor-id=1 ee-mode=1 ee-strength=0 tnr-mode=2 tnr-strength=1 wbmode=3 ! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1,format=NV12 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(width)+', height='+str(height)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! videobalance contrast=1.3 brightness=-.2 saturation=1.2 ! appsink drop=True'
# piCams  OLD Style
camSet2='nvarguscamerasrc sensor-id=0 ! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1,format=NV12 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(width)+', height='+str(height)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink drop=True'
camSet22='nvarguscamerasrc sensor-id=1 ! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1,format=NV12 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(width)+', height='+str(height)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink drop=True'
# webCam  
camSet3 ='v4l2src device=/dev/video2 ! video/x-raw,width='+str(width)+',height='+str(height)+',framerate=20/1 ! videoconvert ! appsink'

cam1=cv2.VideoCapture(camSet1)
cam2=cv2.VideoCapture(camSet3)
while True:
    _, frame1 = cam1.read()
    _, frame2 = cam2.read()
    frame3 = np.hstack((frame1, frame2))
    dt = time.time() - timeMark
    timeMark = time.time()
    dtFIL = .9 * dtFIL + .1 * dt
    fps = 1/dtFIL
    print('fps: ', fps)
    cv2.rectangle(frame3, (0,0), (150,40), (0,0,255), -1)        
    cv2.putText(frame3, 'fps: '  +str(round(fps,1)), (0,30),font,1,(0,255,255),2)    # cv2.imshow('piCam',frame1)
    # cv2.imshow('webCam',frame2)
    cv2.imshow('comboCam',frame3)
    cv2.moveWindow('comboCam',0,450)
    kit.servo[0].angle=pan
    pan = pan + dPan
    if pan >= 179 or pan <= 1:
        dPan = dPan * (-1)
        tilt = tilt + dTilt
        kit.servo[1].angle = tilt
        if tilt >= 169 or tilt <= 11:
            dTilt = dTilt * (-1)
    if cv2.waitKey(1)==ord('q'):
        break
cam1.release()
cam2.release()
cv2.destroyAllWindows()