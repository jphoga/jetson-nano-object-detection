import  face_recognition
import cv2
print(cv2.__version__)
import os
import pickle

Encodings = []
Names = []
image_dir = '/home/jan/code/FaceRecognizer/demoImages/known/'

for root, dirs, files in os.walk(image_dir):
    for file  in files:
        path = os.path.join(root, file)
        name = os.path.splitext(file)[0]
        person = face_recognition.load_image_file(path)
        encoding  = face_recognition.face_encodings(person)[0]
        Encodings.append(encoding)
        Names.append(name)
print(Names)

with open('train_pkl', 'wb') as f:
    pickle.dump(Names, f)
    pickle.dump(Encodings, f)
