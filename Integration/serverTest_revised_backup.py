#Source: https://pyshine.com/Socket-programming-and-openc/
# Welcome to PyShine

# This code is for the server 
# Lets import the libraries
import socket, cv2, pickle,struct, imutils, select, threading
import numpy as np
import serial
import time
import speech_recognition as sr
import pyaudio
import wave
import cv2
import pkg_resources

# Import IPs
import userUI

############################ NEW TEST CODE FOR THREADING #######################################
# from picamera.array import PiRGBArray
# from picamera import PiCamera
from threading import Thread
# from imutils.video.pivideostream import PiVideoStream


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

###########################################################################################################################3
# Socket Create
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tracking_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
audio_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#Avoid address in use error
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tracking_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
audio_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# host_name  = socket.gethostname()
host_ip = userUI.videographer_ip  #socket.gethostbyname(host_name)
# print('HOST IP:',host_ip)
port = 9999
tracking_port = 9998
audio_port = 9997

socket_address = (host_ip,port)
tracking_address = (host_ip,tracking_port)
audio_address = (host_ip,audio_port)

# Socket Bind
server_socket.bind(socket_address)
tracking_socket.bind(tracking_address)
audio_socket.bind(audio_address)

# Socket Listen
server_socket.listen(5)
print("LISTENING AT:",socket_address)
tracking_socket.listen(5)
print("LISTENING AT:",tracking_address)
audio_socket.listen(5)
print("LISTENING AT:",audio_address)


payload_size = struct.calcsize("Q")
previous_message = b''

# Setting up serial communication to robot car
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser.reset_input_buffer()


print("[INFO] sampling THREADED frames")

####### Audio visual set up #######
# vs = PiVideoStream().start()
vs = cv2.VideoCapture(0)
audio = pyaudio.PyAudio()
audio_format = pyaudio.paInt16

audio_stream = audio.open(format=audio_format,channels=userUI.channels, rate=userUI.rate,input=True,frames_per_buffer=userUI.frames_per_buffer)
audio_frames = []
audio_stream.start_stream()

try:
	# Socket Accept
	while True:
		client_socket,addr = server_socket.accept()
		client_tracking_socket,tracking_addr = tracking_socket.accept()
		client_audio_socket,audio_addr = audio_socket.accept()
		print('GOT CONNECTION FROM:',addr)
		print('GOT CONNECTION FROM:',tracking_addr)
		print('GOT CONNECTION FROM:',audio_addr)
		if client_socket and client_tracking_socket and client_audio_socket:
			client_tracking_socket.setblocking(0)
			# client_socket.setblocking(0)
			# client_audio_socket.setblocking(0)
			while(vs):
				# print("sample size: ")
				# print(audio.get_sample_size(audio_format))
				#### Camera frame capture and transmission ####
				ret,frame = vs.read()
				if ret != True:
					continue
				# print('here')
				frame = imutils.resize(frame,width=320,inter=cv2.INTER_LANCZOS4)
				
				a = pickle.dumps(frame)
				message = struct.pack("Q",len(a))+a
				if( np.shape(frame)==()):
					# print(message)
					continue
				try:
					client_socket.sendall(message)
					# print("camera success")
				except:
					# print("camera error")
					pass
				
				#### Audio capture and transmission ###
				audio_data = audio_stream.read(userUI.frames_per_buffer)
				audio_a = pickle.dumps(audio_data)
				audio_message = struct.pack("Q",len(audio_a)) + audio_a
				try:
					client_audio_socket.sendall(audio_message)
					# print("microphone success")
				except:
					# print("microphone error")
					pass



				while True:
					try:
						client_message = client_tracking_socket.recv(4096)
						if client_message:
							ser.write(client_message)
							print(client_message)
						# else:
						# 	print("nope")
					except:
						break

					# if "start" in command:
					# 	client_speech_socket.sendall(b"Start Recording\n")
					# 	print("Start Recording")
					# 	command = "m"

					# if "stop" in command:
					# 	client_speech_socket.sendall(b"Stop Recording\n")
					# 	print("Stop Recording")
					# 	command = "m"

					# if "calibrate" in command:
					# 	client_speech_socket.sendall(b"Calibrate\n")
					# 	print("Calibrating")
					# 	command = "m"
											
finally:
	# vs.release()
	cv2.destroyAllWindows()
	server_socket.close()
'''   
def hear():
    time.sleep(10)
    
    while(True):
        
        global command
		
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)

        try:
            command = r.recognize_google(audio)
            print("Google Speech Recognition thinks you said " + command)

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
'''
# if __name__ == '__main__':
# 	server()
    # t1 = threading.Thread(target=server)
    # t2 = threading.Thread(target=hear)

    # t1.start()
    # t2.start()

    # t1.join()
    # t2.join()