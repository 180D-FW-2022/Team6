This folder contains the library project folder for gesture recognition found at https://techvidvan.com/tutorials/hand-gesture-recognition-tensorflow-opencv/.

This code analyzes OpenCV frames and recognizes the gestures listed here: Gesture\hand-gesture-recognition-code\gesture.names
Once recognized, the program prints the name of the gesture recognized in the output OpenCV frame. 

A current issue is that the software is always "recognizing" some gesture if there is a hand in frame, even if no gesture is being performed. Additionally, some similar gestures like "Stop" and "Live Long" are mischaracterized to be each other. In our final project, we plan to limit the gestures the program looks for to avoid this mischaracterization.

Additionally the code only recognizes gestures on one hand at a time. In the future, we hope to expand that to any hand in frame.

To run this code, run the file located here: Gesture\hand-gesture-recognition-code\TechVidvan-hand_gesture_detection.py