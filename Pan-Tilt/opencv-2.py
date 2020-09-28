import time
from adafruit_servokit import ServoKit
kit=ServoKit(channels=16)
tilt=125
pan=0
kit.servo[0].angle=pan
kit.servo[1].angle=tilt
for i in range(0,180):
    kit.servo[0].angle=i
    time.sleep(.05)
for i in range(180,0,-1):
    kit.servo[0].angle=i
    time.sleep(.05)
for i in range(45,180):
    kit.servo[1].angle=i
    time.sleep(.05)
for i in range(180,0,-1):
    kit.servo[1].angle=i
    time.sleep(.05)