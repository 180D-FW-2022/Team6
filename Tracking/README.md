Tracking + Hardware:

The tracking code was adapted from: https://towardsdatascience.com/real-time-object-tracking-with-tensorflow-raspberry-pi-and-pan-tilt-hat-2aeaef47e134

The pan-tilt HAT included servo controlling code provided by the pan-tilt HAT company Waveshare: https://github.com/waveshare/Pan-Tilt-HAT

The purpose of this software is to track a person's face during a video recording. If a person's face leaves the center of the frame, the code will prompt the servos on the pan-tilt hardware to adjust in order to recenter the subject of the video.

This code is for face detection using OpenCV. The following libraries are imported:

numpy: for numerical calculations
cv2: for computer vision operations
os: for interacting with the operating system
curses: for terminal screen control
time: for time-related functions
PCA9685: for controlling a servo using PWM
The code then loads a pre-trained Haar cascade classifier from the OpenCV library to detect faces. It captures frames from a video feed and applies the face detector on each frame. If a face is detected, it draws a rectangle around the face and displays the frame. The code also includes a pseudo-PID control algorithm to move the servo in response to the movement of the detected face.

To run the code, the user must have the necessary libraries installed, as well as a servo connected to the PCA9685 module. The cascade classifier must also be in the specified path.

The main file is pan_tracking_v1.py in the Final Tracking folder. The main function is cascadeclassifier from the OpenCV library. The function gives the (x,y,w,h) information of a person's face in the frame. (X,Y) is the position of the top left corner of the person's face whereas (w,h) are the width and height of a perosn's face, respectively. This information is then used to detect the center of a person's face which we can use to control the pan tilt servos.

One main error we encountered was with the downloading of the /data/haarcascade_frontalface_default.xml. In order to resolve this issue, the user must search for where the .xml file is downloaded on their raspberry pi and replace the path name.

Tracking + Hardware:

The tracking code was adapted from: https://towardsdatascience.com/real-time-object-tracking-with-tensorflow-raspberry-pi-and-pan-tilt-hat-2aeaef47e134

The pan-tilt HAT included servo controlling code provided by the pan-tilt HAT company Waveshare: https://github.com/waveshare/Pan-Tilt-HAT

The purpose of this software is to track a person's face during a video recording. If a person's face leaves the center of the frame, the code will prompt the servos on the pan-tilt hardware to adjust in order to recenter the subject of the video.

The main file is pan_tracking_v1.py in the Final Tracking folder. The main function is cascadeclassifier from the OpenCV library. The function gives the (x,y,w,h) information of a person's face in the frame. (X,Y) is the position of the top left corner of the person's face whereas (w,h) are the width and height of a perosn's face, respectively. This information is then used to detect the center of a person's face which we can use to control the pan tilt servos.

One main error we encountered was with the downloading of the /data/haarcascade_frontalface_default.xml. In order to resolve this issue, the user must search for where the .xml file is downloaded on their raspberry pi and replace the path name.