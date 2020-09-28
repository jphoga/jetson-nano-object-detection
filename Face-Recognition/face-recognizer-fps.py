import face_recognition
import cv2
import  os
import pickle
import time
print(cv2.__version__)

width = 640
height = 480
flip = 2
fpsReport = 0
scaleFactor = 0.25

Encodings = []
Names = []


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


cam = cv2.VideoCapture(camSet1old)
font =  cv2.FONT_HERSHEY_SIMPLEX

print("INFO: Start  reading frames...")
timeStamp = time.time()
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
    dt = time.time() - timeStamp
    fps = 1 / dt
    fpsReport = .90 * fpsReport + .1 *fps 
    print('FPS: ', round(fpsReport, 1))
    timeStamp =  time.time()
    cv2.rectangle(frame, (0,0),(100,40),(0,0,255), -1)
    cv2.putText(frame, str(round(fpsReport, 1)) + ' fps',(0, 25), font, .75,  (0, 255,255), 2)
    cv2.imshow('Picture', frame)
    cv2.moveWindow('Picture', 0,0)
    if cv2.waitKey(1) == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()
