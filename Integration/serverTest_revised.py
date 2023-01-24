#Source: https://pyshine.com/Socket-programming-and-openc/
# Welcome to PyShine

# This code is for the server 
# Lets import the libraries
import socket, cv2, pickle,struct, imutils, select
import numpy as np

#################################################### Pan-Tilt Tracking Initializations ######################################################################

import numpy
import cv2
from PCA9685 import PCA9685


import pkg_resources

############################ NEW TEST CODE FOR THREADING #######################################
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
from imutils.video.pivideostream import PiVideoStream

###### troubleshooting hanging receive
import sys, fcntl, os, errno
from time import sleep

#setting start up serrvo positions
# ========================================================================
# pwm = PCA9685()
# pwm.setPWMFreq(50)

current_PAN  = 90
current_TILT = 60
payload_size = struct.calcsize("Q")
# pwm.setRotationAngle(1, current_PAN) #PAN    
# pwm.setRotationAngle(0, current_TILT) #TILT

######################################################################### End of Pan-Tilt Tracking Initializations ####################################################################################

class PiVideoStream:
	def __init__(self, resolution=(320, 240), framerate=32):
		# initialize the camera and stream
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = framerate
		self.rawCapture = PiRGBArray(self.camera, size=resolution)
		self.stream = self.camera.capture_continuous(self.rawCapture,
			format="bgr", use_video_port=True)
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
		for f in self.stream:
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			self.frame = f.array
			self.rawCapture.truncate(0)
			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			if self.stopped:
				self.stream.close()
				self.rawCapture.close()
				self.camera.close()
				return

	def read(self):
		# return the frame most recently read
		return self.frame
	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

print("[INFO] sampling THREADED frames from `picamera` module...")
vs = PiVideoStream().start()

###########################################################################################################################3
# Socket Create
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name  = socket.gethostname()
host_ip = '169.232.126.22' #socket.gethostbyname(host_name)
print('HOST IP:',host_ip)
port = 9999
socket_address = (host_ip,port)

# Socket Bind
server_socket.bind(socket_address)

# Socket Listen
server_socket.listen(5)
print("LISTENING AT:",socket_address)

try:
	# Socket Accept
	while True:
		client_socket,addr = server_socket.accept()
		# client_socket.setblocking(0)
		print('GOT CONNECTION FROM:',addr)
		if client_socket:
			while(vs):
				frame = vs.read()
				frame = imutils.resize(frame,width=320,inter=cv2.INTER_LANCZOS4)
				
				a = pickle.dumps(frame)
				message = struct.pack("Q",len(a))+a
				if( np.shape(frame)==()):
					# print(message)
					continue
				client_socket.sendall(message)
				# while True:
					
				# 	print('1')
				# 	try:
				# 		print('2')
				# 		from_client = ''
				# 		print(client_socket.recv(4096))
				# 		client_message = client_socket.recv(4096)
				# 		print('3')
				# 		# if not client_message: break
				# 		print('4')
				# 		from_client += client_message.decode('utf_8')
				# 		print('5')
				# 		print(from_client)
				# 	except socket.error as e:
				# 		err = e.args[0]
				# 		if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
				# 			sleep(1)
				# 			print ('No data available')
				# 			continue
				# 		else:
				# 			# a "real" error occurred
				# 			print (e)
				# 			sys.exit(1)
				# 	else:
				# 		print("success")
					
					# from_client = client_socket.recv(4096).decode()
					# print(from_client)						
finally:
	# shut down cleanly
    # pwm.exit_PCA9685()
    
    # vs.release()
    cv2.destroyAllWindows()