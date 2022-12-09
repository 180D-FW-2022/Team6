This folder contains the integration of all our subsystems. It succesfully transmits camera data from the server device (raspberry pi) to the client device (laptop). It recognizes voice commands on the client device, performs gesture recognition on the client device, and performs facial tracking and motor actuation on the server device.

While functional in its current state, there exists a 5 second lag between the server and client device. We hope to resolve this issue in the next quarter.

To run this code, first ensure that both the raspberry pi and laptop are connected to the same wifi. Next, update the ip address in serverTest.py and clientTest.py to that of the raspberry pi collecting camera data and equipped with the pan-tilt device. Next, run serverTest.py on the raspberry pi and clientTest.py on the laptop to see the unmanned videographer at work.

The laptop will display the gesture recognition, prompt the user for voice commands, and display facial tracking data.

The tracking code was adapted from: https://towardsdatascience.com/real-time-object-tracking-with-tensorflow-raspberry-pi-and-pan-tilt-hat-2aeaef47e134  

The pan-tilt HAT included servo controlling code provided by the pan-tilt HAT company Waveshare: https://github.com/waveshare/Pan-Tilt-HAT 

The communication code was adapted from: https://pyshine.com/Socket-programming-and-openc/