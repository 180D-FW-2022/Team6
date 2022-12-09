This folder contains (3) iterations of our communication software. Each one attempts to stream camera data from the server device to the client device for display.

client.py/server.py contain code adapted from the solution at https://medium.com/@pritam.mondal.0711/stream-live-video-from-client-to-server-using-opencv-and-paho-mqtt-674d3327e8b3. It utilizes the MQTT protocol and has a significant delay of 5+ min for data streaming. This was our first iteration.

socketClient.py/socketServer.py contain code adapted from the solution at https://bruinlearn.ucla.edu/courses/140361/modules utilized in our Week 3 Lab. This iteration only sent one frame of camera data before stopping. This was our second iteration.

clientTest.py/serverTest.py contain are current working iteration and contain code adapted from the solution at https://pyshine.com/Socket-programming-and-openc/. There remains a few seconds lag in this iteration that hopefully will be resolved in the winter quarter.