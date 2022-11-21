
import numpy
import cv2
import os
import curses
import time
from PCA9685 import PCA9685

# Load the cascade
# ========================================================================
# faceCascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
# faceCascade.load('data/haarcascade_frontalface_default.xml')

cascPath=os.path.dirname(cv2.__file__)+"/data/haarcascade_frontalface_default.xml"
#cascPath=os.path.dirname(cv2.__file__)+"/data/haarcascade_eye_tree_eyeglasses.xml"

faceCascade = cv2.CascadeClassifier(cascPath)
# Read the input image
print(cascPath)

print("step 1")
# Define a video capture object
video_capture = cv2.VideoCapture(0)
print ("step2")

while True:
    # capture the video frame by frame
    ret, frame = video_capture.read()

    # Display the resulting frame
    v2.imshow('face_tracking', frame)  

    # q is pressed, then quit 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# after loop release the capture object
video_capture.release()

# destroy all the windows
cv2.destroyAllWindows()
