#!/usr/bin/env python
# coding: utf-8

# my code, callibration for desired face area

# In[16]:


## Calibration code

import cv2
import numpy as np

# Load the cascade for face detection
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Start the video capture
cap = cv2.VideoCapture(0)

# Set the initial position of the motor
initial_position = 0

desired_face_area = 0 
current_face_area = 0

def callibrateDistance:
    print("callibration completed")
    desired_face_area = (x+w)*(y+h)
    return desired_face_area

while True:
    
    # Read the frame
    _, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray,scaleFactor=1.2, minNeighbors=4, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
    
    areas=[]
   
    # TODO: check if there is anything inside faces
        
    if np.any(faces): # faces is not empty
        # find the largest face 
        if (len(faces)>1): # if there are more than one face
            for (x, y, w, h) in faces:
                areas.append((x+w)*(y+h))

            print("area list:")
            print(areas)

            maxArea = max(areas)
            maxAreaPos = areas.index(maxArea)

            print("max area:")
            print(maxArea)
            face = faces[maxAreaPos] #largest face
        elif (len(faces)==1):
            face = faces[0]
        
        (x,y,w,h) = face 
        
        
        # Draw a rectangle around the faces
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
        # Get the center of the face
        face_center_x = x + w/2
        face_center_y = y + h/2
            
        
        # calculate the area of the desired face rectangle (give an error of +/- 50)
        desired_face_area = (x+w)*(y+h)
    
        # Calculate the error from the center of the frame
        error_x = frame.shape[1]/2 - face_center_x
        error_y = frame.shape[0]/2 - face_center_y
        
        # Move the motor to recenter the camera
        # Replace this with your specific motor control code
        # This is just an example


        #move_motor(initial_position + error_x, initial_position + error_y)

        # need to move the motor back and forth
        
   
        
    else: #faces empty
        print("faces empty")
    
    # Show the frame
    cv2.imshow("Face Tracking", frame)

    # Exit if the 'b' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('b'):
        break

# Release the video capture
cap.release()

# Close all windows
cv2.destroyAllWindows()

print("final desired face area:")
print(desired_face_area)


# sarah: make 10,000 the threshold face area that would not encounter change
# below code is about the moving forwards and backwards
# todo: increase tolerance and threshold.

# In[4]:


import cv2
import numpy as np


# Load the cascade for face detection
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Start the video capture
cap = cv2.VideoCapture(0)

# Set the initial position of the motor
initial_position = 0

desired_face_area = 0
current_face_area = 0
callibrated = False
moving = False

while True:
    
    # Read the frame
    _, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray,scaleFactor=1.2, minNeighbors=4, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

    areas=[]
    if np.any(faces): # faces is not empty
        # find the largest face 
        if (len(faces)>1): # if there are more than one face
            for (x, y, w, h) in faces:
                areas.append((x+w)*(y+h))

            maxArea = max(areas)
            maxAreaPos = areas.index(maxArea)

            face = faces[maxAreaPos] #largest face
        elif (len(faces)==1):
            face = faces[0]
    
        (x,y,w,h) = face 

        # Draw a rectangle around the faces
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Get the center of the face
        face_center_x = x + w/2
        face_center_y = y + h/2
        
        # field of view center
        frame_center_x = frame.shape[1]/2
        frame_center_y = frame.shape[0]/2

        # calculate the area of the desired face rectangle
        current_area = (x+w)*(y+h)
        
        # Calculate the error from the center of the frame
        error_x = frame_center_x - face_center_x
        error_y = frame_center_y - face_center_y
        
        print("error_x")
        print(error_x)
        
        # left and right motion
        if (error_x>10): #TODO: include tolerances
            print("turn right") 
            moving = True
        elif (error_x<10):
            print("turn left") #todo: directions might be wrong
            moving = True
        else:
            moving = False
        
        # callibrate
        if cv2.waitKey(1) & 0xFF == ord('b'):
            desired_face_area = current_area
            callibrated = True
            
        print("desired_face_area")
        print(desired_face_area)

        print("current_faca_area")
        print(current_area)
        
        if callibrated:
            if (current_area - desired_face_area > 100000): #TODO: can change the tolerance
                print("zoom out")
                moving = True
            elif (current_area - desired_face_area<-100000):
                print("zoom in")
                moving = True
            else:
                moving = False
        else:
            print ("not callibrated")
        
        if not moving:
            print ("stop")

    else: #faces empty
        print("faces empty")

    # Show the frame
    cv2.imshow("Face Tracking", frame)

    # Exit if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture
cap.release()

# Close all windows
cv2.destroyAllWindows()

