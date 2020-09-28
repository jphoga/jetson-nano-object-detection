import cv2
import jetson.inference
import jetson.utils
import time
import numpy as np

from adafruit_servokit import ServoKit
scanMode  = True
# Modify for faster servo movement (highe number => more stable but slower)
servoScaleFactor = 40
kit=ServoKit(channels=16)
tilt=90
pan=90
dTilt=10
dPan=1
kit.servo[0].angle=pan
kit.servo[1].angle=tilt

timeStamp=time.time()
fpsFilter = 0
dispW = 1024
dispH  = 720
flip = 2
font = cv2.FONT_HERSHEY_SIMPLEX

####  Gstreamer code for improvded Raspberry Pi Camera Quality
# piCams  NEW Style
camSet0new='nvarguscamerasrc sensor-id=0 ee-mode=1 ee-strength=0 tnr-mode=2 tnr-strength=1 wbmode=3 ! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1,format=NV12 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! videobalance contrast=1.3 brightness=-.2 saturation=1.2 ! appsink drop=True'
camSet1new='nvarguscamerasrc sensor-id=1 ee-mode=1 ee-strength=0 tnr-mode=2 tnr-strength=1 wbmode=3 ! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1,format=NV12 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! videobalance contrast=1.3 brightness=-.2 saturation=1.2 ! appsink drop=True'
# piCams  OLD Style
camSet0old='nvarguscamerasrc sensor-id=0 ! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1,format=NV12 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink drop=True'
camSet1old='nvarguscamerasrc sensor-id=1 ! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1,format=NV12 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink drop=True'
# webCam  
camSet2web ='v4l2src device=/dev/video2 ! video/x-raw,width='+str(dispW)+',height='+str(dispH)+',framerate=20/1 ! videoconvert ! appsink drop=True'

cam = cv2.VideoCapture(camSet1new)

###  Webcam
# cam = cv2.VideoCapture('/dev/video1')
# cam.set(cv2.CAP_PROP_FRAME_WIDTH, dispW)
# cam.set(cv2.CAP_PROP_FRAME_WIDTH, dispH)

net = jetson.inference.detectNet('ssd-mobilenet-v2', threshold  = .5)

while True:
    _,img = cam.read()
    height = img.shape[0]
    width = img.shape[1]
    frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)
    frame = jetson.utils.cudaFromNumpy(frame)
    detections = net.Detect(frame, width, height)
    for  detect in detections:
        ID = detect.ClassID
        top = int(detect.Top)
        left = int(detect.Left)
        bottom = int(detect.Bottom)
        right = int(detect.Right)
        item = net.GetClassDesc(ID)
        # print(item, top, left, bottom, right)
        tk = 3
        if item == 'person':
            # tk = -1
            cv2.rectangle(img, (left, top), (right, bottom), (0,255,0), tk)
            cv2.putText(img, item, (left, top + 20),font,1,(0,0,255),2)
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
    timeStamp = time.time()
    fps = 1/dt
    fpsFilter = .9 * fpsFilter + .1 * fps
    cv2.putText(img,str(round(fpsFilter,1)) + ' fps ',(0,30),font,1,(0,0,255),2)
    cv2.imshow('detCam',img)
    cv2.moveWindow('detCam',0,0)
    if cv2.waitKey(1)==ord('q'):
        break
cam.releast()
cv2.destroyAllWindows()