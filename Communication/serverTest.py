#Source: https://pyshine.com/Socket-programming-and-openc/
#Source for new test code: https://pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/

# Welcome to PyShine

# This code is for the server 
# Lets import the libraries
import socket, cv2, pickle,struct,imutils
import numpy as np

############################ NEW TEST CODE FOR THREADING #######################################
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
# from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
import argparse
import time

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

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,
	help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
	help="Whether or not frames should be displayed")
args = vars(ap.parse_args())
# initialize the camera and stream
# camera = PiCamera()
# camera.resolution = (320, 240)
# camera.framerate = 32
# rawCapture = PiRGBArray(camera, size=(320, 240))
# stream = camera.capture_continuous(rawCapture, format="bgr",
# 	use_video_port=True)

# created a *threaded *video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from `picamera` module...")
vs = PiVideoStream().start()
# time.sleep(2.0)
# fps = FPS().start()
# loop over some frames...this time using the threaded stream
# while True:
# 	# grab the frame from the threaded video stream and resize it
# 	# to have a maximum width of 400 pixels
# 	frame = vs.read()
# 	# frame = imutils.resize(frame, width=320,inter=cv2.INTER_LANCZOS4)
# 	# check to see if the frame should be displayed to our screen
# 	if args["display"] > 0:
# 		cv2.imshow("Frame", frame)
# 		key = cv2.waitKey(1) & 0xFF
# 	# update the FPS counter
# 	# fps.update()
# # stop the timer and display FPS information
# # fps.stop()
# # print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
# # print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
# # do a bit of cleanup
# cv2.destroyAllWindows()
# vs.stop()

###########################################################################################################################3
# Socket Create
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name  = socket.gethostname()
host_ip = '169.232.242.106' #socket.gethostbyname(host_name)
print('HOST IP:',host_ip)
port = 9999
socket_address = (host_ip,port)

# Socket Bind
server_socket.bind(socket_address)

# Socket Listen
server_socket.listen(5)
print("LISTENING AT:",socket_address)

# Socket Accept
while True:
	client_socket,addr = server_socket.accept()
	print('GOT CONNECTION FROM:',addr)
	if client_socket:
		# vid = cv2.VideoCapture(0)
		
		while(vs):
			# img,frame = vid.read()
			frame = vs.read()
			frame = imutils.resize(frame,width=320,inter=cv2.INTER_LANCZOS4)
			
			a = pickle.dumps(frame)
			message = struct.pack("Q",len(a))+a
			if( np.shape(frame)==()):
				# print(message)
				continue
			client_socket.sendall(message)
			
			# cv2.imshow('TRANSMITTING VIDEO',frame)
			# key = cv2.waitKey(1) & 0xFF
			# if key ==ord('q'):
			# 	client_socket.close()	
					
# # Socket Accept
# while True:
# 	client_socket,addr = server_socket.accept()
# 	print('GOT CONNECTION FROM:',addr)
# 	if client_socket:
# 		vid = cv2.VideoCapture(0)
		
# 		while(vid.isOpened()):
# 			img,frame = vid.read()
# 			frame = imutils.resize(frame,width=320,inter=cv2.INTER_LANCZOS4)
			
# 			a = pickle.dumps(frame)
# 			message = struct.pack("Q",len(a))+a
# 			if( np.shape(frame)==()):
# 				# print(message)
# 				continue
# 			client_socket.sendall(message)
			
# 			# cv2.imshow('TRANSMITTING VIDEO',frame)
# 			# key = cv2.waitKey(1) & 0xFF
# 			# if key ==ord('q'):
# 			# 	client_socket.close()	