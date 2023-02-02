#!/usr/bin/env python
# coding: utf-8

# sarah: make 10,000 the threshold face area that would not encounter change
# below code is about the moving forwards and backwards
# todo: increase tolerance and threshold.

# In[4]:


import cv2, serial, time
import numpy as np

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser.reset_input_buffer()

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

# Delete later

while True:
    #Delete later
    count = count + 1
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
        if (error_x>60): #TODO: include tolerances
            ser.write(b"LEFTT\n") 
            moving = True
        elif (error_x<-60):
            ser.write(b"RIGHT\n") #todo: directions might be wrong
            moving = True
        else:
            moving = False
        
        # callibrate
        #Delete later
        if not callibrated: #cv2.waitKey(1) & 0xFF == ord('b'):
            desired_face_area = current_area
            callibrated = True
            
        print("desired_face_area")
        print(desired_face_area)

        print("current_face_area")
        print(current_area)
        
        if callibrated:
            if (current_area - desired_face_area > 100000): #TODO: can change the tolerance
                ser.write(b"BACK\n")
                moving = True
            elif (current_area - desired_face_area<-100000):
                ser.write(b"FRONT\n")
                moving = True
            else:
                moving = False
        else:
            print ("not callibrated")
        
        if not moving:
            ser.write(b"STOP\n")

    else: #faces empty
        print("faces empty")

    # Show the frame
    # cv2.imshow("Face Tracking", frame)

    # # Exit if the 'q' key is pressed
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# Release the video capture
cap.release()

# Close all windows
cv2.destroyAllWindows()

