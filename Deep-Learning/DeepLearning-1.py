import  jetson.inference
import  jetson.utils
import cv2
import numpy as np
import  time


flip = 2
piWidth = 1280
piHeight = 720
webWidth = 640
webHeight = 480
width = 1280
height = 720

## Raspi Cam with cv2
camSet='nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(piWidth)+', height='+str(piHeight)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'
# cam = cv2.VideoCapture(camSet)

## Web Cam with cv2
cam = cv2.VideoCapture('/dev/video1')
cam.set(cv2.CAP_PROP_FRAME_WIDTH,webWidth)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT,webHeight)

## Raspi Cam with gstream
# cam = jetson.utils.gstCamera(piWidth,  piHeight, 'csi://0')

## Web Cam with gstream
# cam = jetson.utils.gstCamera(webWidth,  webHeight, '/dev/video1')

net = jetson.inference.imageNet("googlenet")
timeMark = time.time()
fpsFilter  = 0
font = cv2.FONT_HERSHEY_SIMPLEX

while True:
    ## GSTREAM
    # frame, width, height = cam.CaptureRGBA(zeroCopy=1)

    ## CV2
    _, frame = cam.read()
    img  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA).astype(np.float32)
    img = jetson.utils.cudaFromNumpy(img)

    ## GSTREAM
    # classID, confidence = net.Classify(frame, width, height)
    
    ## CV2
    classID, confidence = net.Classify(img, width, height)
    
    item = net.GetClassDesc(classID)
    dt = time.time() - timeMark
    fps = 1/dt
    fpsFilter = .95 * fpsFilter + .05 * fps 
    timeMark = time.time()

    ## GSTREAM
    # frame = jetson.utils.cudaToNumpy(frame, width, height, 4)
    # frame = cv2.cvtColor(frame,  cv2.COLOR_RGB2BGR).astype(np.uint8)
    
    cv2.putText(frame, str(round(fpsFilter, 1)) + ' fps ' + item, (0,30), font, 1, (0,0,255), 2)
    cv2.imshow('recCam', frame)
    cv2.moveWindow('Picture', 0,0)
    if cv2.waitKey(1) == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()

    # font.OverlayText(frame,  width, height, str(round(fpsFilter, 1)) + " fps " + item, 5,5,font.Magenta, font.Blue)
    # display.RenderOnce(frame, width, height)

