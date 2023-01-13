Tracking + Hardware:

The tracking code was adapted from: https://towardsdatascience.com/real-time-object-tracking-with-tensorflow-raspberry-pi-and-pan-tilt-hat-2aeaef47e134

The pan-tilt HAT included servo controlling code provided by the pan-tilt HAT company Waveshare: https://github.com/waveshare/Pan-Tilt-HAT

The purpose of this software is to track a person's face during a video recording. If a person's face leaves the center of the frame, the code will prompt the servos on the pan-tilt hardware to adjust in order to recenter the subject of the video.

The main file is pan_tracking_v1.py in the Final Tracking folder. The main function is cascadeclassifier from the OpenCV library. The function gives the (x,y,w,h) information of a person's face in the frame. (X,Y) is the position of the top left corner of the person's face whereas (w,h) are the width and height of a perosn's face, respectively. This information is then used to detect the center of a person's face which we can use to control the pan tilt servos.

One main error we encountered was with the downloading of the /data/haarcascade_frontalface_default.xml. In order to resolve this issue, the user must search for where the .xml file is downloaded on their raspberry pi and replace the path name.