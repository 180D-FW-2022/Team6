### SERVER


#Source: https://pyshine.com/Socket-programming-and-openc/
# Welcome to PyShine

# This code is for the server 
# Lets import the libraries
import socket, cv2, pickle,struct, imutils, select
import numpy as np
import serial
import time

import pkg_resources

############################ NEW TEST CODE FOR THREADING #######################################
# from picamera.array import PiRGBArray
# from picamera import PiCamera
from threading import Thread
# from imutils.video.pivideostream import PiVideoStream

###### troubleshooting hanging receive
# import sys, fcntl, os, errno
# from time import sleep


class PiVideoStream:
	def __init__(self, resolution=(320, 240), framerate=32):
		# # initialize the camera and stream
		# self.camera = PiCamera()
		# self.camera.resolution = resolution
		# self.camera.framerate = framerate
		# self.rawCapture = PiRGBArray(self.camera, size=resolution)
		# self.stream = self.camera.capture_continuous(self.rawCapture,
		# 	format="bgr", use_video_port=True)
		self.stream = cv2.VideoCapture(0)
		self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
		self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
		self.stream.set(cv2.CAP_PROP_FPS, 10)
		# initialize the frame and the variable used to indicate
		# if the thread should be stopped
		self.frame = None
		self.stopped = False

	def start(self):
		# start the thread to read frames from the video stream
		Thread(target=self.update, args=()).start()
		return self
	def update(self):
		# keep looping infinitely until the thread is stopped
		while self.stream:
			f = self.stream
			_, self.frame = f.read()
		# for f in self.stream:
		# 	# grab the frame from the stream and clear the stream in
		# 	# preparation for the next frame
		# 	self.frame = f.array
		# 	self.rawCapture.truncate(0)
		# 	# if the thread indicator variable is set, stop the thread
		# 	# and resource camera resources
		# 	if self.stopped:
		# 		self.stream.close()
		# 		# self.rawCapture.close()
		# 		# self.camera.close()
		# 		return

	def read(self):
		# return the frame most recently read
		return self.frame
	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

previous_message = b''

# Setting up serial communication to robot car
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser.reset_input_buffer()

print("[INFO] sampling THREADED frames from `picamera` module...")
vs = PiVideoStream().start()
# vs = cv2.VideoCapture(0)

###########################################################################################################################3
# Socket Create

####### TCP
#server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # TCP (SOCK_STREAM)
#tracking_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 

###### UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP (SOCK_DGRAM)
tracking_socket = socket.socket(socket.AF_INET,socet.SOCK_DGRAM)

 
#Avoid address in use error
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tracking_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# host_name  = socket.gethostname()
host_ip = '164.67.233.31' #socket.gethostbyname(host_name)
# print('HOST IP:',host_ip)

port = 9999
tracking_port = 9998

socket_address = (host_ip,port)
tracking_address = (host_ip,tracking_port)

# Socket Bind
server_socket.bind(socket_address)
tracking_socket.bind(tracking_address)

# Socket Listen
server_socket.listen(5)
print("LISTENING AT:",socket_address)
tracking_socket.listen(5)
print("LISTENING AT:",tracking_address)

try:
	# Socket Accept
	while True:
		client_socket,addr = server_socket.accept()
		client_tracking_socket,tracking_addr = tracking_socket.accept()
		print('GOT CONNECTION FROM:',addr)
		print('GOT CONNECTION FROM:',tracking_addr)
		if client_socket and client_tracking_socket:
			client_tracking_socket.setblocking(0)
			while(vs):
				frame = vs.read()
				frame = imutils.resize(frame,width=320,inter=cv2.INTER_LANCZOS4)
				
				a = pickle.dumps(frame)
				message = struct.pack("Q",len(a))+a
				if( np.shape(frame)==()):
					# print(message)
					continue
				client_socket.sendall(message)
				
				while True:
					
					# print('1')
					try:
						# print('2')
						from_client = ''
						client_message = client_tracking_socket.recv(4096)
						if client_message:# != previous_message:
							# client_socket.setblocking(1)
							# from_client = str(client_message)
							# previous_message = client_message
							ser.write(client_message)
							# print(client_message)
						# else:
						# 	print("nope")
					except socket.error as e:
						break
						# err = e.args[0]
						# if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
						# 	# sleep(1)
						# 	# print ('No data available')
						# 	break
						# 	# continue
						# else:
						# 	# a "real" error occurred
						# 	# print (e)
						# 	sys.exit(1)
											
finally:
	# shut down cleanly
    # pwm.exit_PCA9685()
    
    # vs.release()
	cv2.destroyAllWindows()
	server_socket.close()
    