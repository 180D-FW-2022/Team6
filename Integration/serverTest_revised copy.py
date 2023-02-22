#Source: https://pyshine.com/Socket-programming-and-openc/
# Welcome to PyShine

# This code is for the server 
# Lets import the libraries
import socket, cv2, pickle,struct, imutils, select
import numpy as np
import serial
import speech_recognition as sr
import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os
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

class VideoRecorder():
	
	
	
	# Video class based on openCV 
	def __init__(self):
		
		self.open = True
		self.device_index = 0
		self.fps = 5.6               # fps should be the minimum constant rate at which the camera can
		self.fourcc = "MJPG"       # capture images (with no decrease in speed over time; testing is required)
		self.frameSize = (640,480) # video formats and sizes also depend and vary according to the camera used
		self.video_filename = "temp_video.avi"
		self.video_cap = cv2.VideoCapture(self.device_index)
		self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
		self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frameSize)
		self.frame_counts = 1
		self.start_time = time.time()

	
	# Video starts being recorded 
	def record(self):
		###########################################################################################################################3
		# Socket Create
		server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		tracking_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		# speech_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

		#Avoid address in use error
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		tracking_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# speech_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# host_name  = socket.gethostname()
		host_ip = userUI.videographer_ip  #socket.gethostbyname(host_name)
		# print('HOST IP:',host_ip)
		port = 9999
		tracking_port = 9998
		# speech_port = 9997

		socket_address = (host_ip,port)
		tracking_address = (host_ip,tracking_port)
		# speech_address = (host_ip,speech_port)

		# Socket Bind
		server_socket.bind(socket_address)
		tracking_socket.bind(tracking_address)
		# speech_socket.bind(speech_address)

		# Socket Listen
		server_socket.listen(5)
		print("LISTENING AT:",socket_address)
		tracking_socket.listen(5)
		print("LISTENING AT:",tracking_address)
		# speech_socket.listen(5)
		# print("LISTENING AT:",speech_address)


		payload_size = struct.calcsize("Q")
		previous_message = b''

		# Setting up serial communication to robot car
		# ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
		# ser.reset_input_buffer()

		print("[INFO] sampling THREADED frames from `picamera` module...")
		# vs = PiVideoStream().start()
		# vs = cv2.VideoCapture(0)

#		counter = 1
		timer_start = time.time()
		timer_current = 0
		try:
			# Socket Accept
			while True:
				client_socket,addr = server_socket.accept()
				client_tracking_socket,tracking_addr = tracking_socket.accept()
				# client_speech_socket,speech_addr = speech_socket.accept()
				print('GOT CONNECTION FROM:',addr)
				print('GOT CONNECTION FROM:',tracking_addr)
				# print('GOT CONNECTION FROM:',speech_addr)
				if client_socket and client_tracking_socket: # and client_speech_socket:
					client_tracking_socket.setblocking(0)
					print('5')
					client_socket.setblocking(0)
					# client_speech_socket.setblocking(0)
					
					while(self.open==True):
						ret, video_frame = self.video_cap.read()
						if (ret==True):
				
								self.video_out.write(video_frame)
								self.frame_counts += 1

								time.sleep(0.16)
						else:
							break

						frame = imutils.resize(video_frame,width=320,inter=cv2.INTER_LANCZOS4)
						
						a = pickle.dumps(frame)
						message = struct.pack("Q",len(a))+a
						if( np.shape(frame)==()):
							# print(message)
							continue
						try:
							client_socket.sendall(message)
						except:
							# print("error")
							continue
						
						while True:
							try:
								client_message = client_tracking_socket.recv(4096)
								if client_message:
									a=1 #dummy placeholder
									# ser.write(client_message)
									# print(client_message)
								# else:
								# 	print("nope")
							except:
								break
													
		finally:
			# vs.release()
			cv2.destroyAllWindows()
			server_socket.close()				

	# Finishes the video recording therefore the thread too
	def stop(self):
		
		if self.open==True:
			
			self.open=False
			self.video_out.release()
			self.video_cap.release()
			cv2.destroyAllWindows()
			
		else: 
			pass


	# Launches the video recording function using a thread			
	def start(self):
		video_thread = threading.Thread(target=self.record)
		video_thread.start()

class AudioRecorder():
	

    # Audio class based on pyAudio and Wave
    def __init__(self):
        
        self.open = True
        self.rate = 44100
        self.frames_per_buffer = 1024
        self.channels = 2
        self.format = pyaudio.paInt16
        self.audio_filename = "temp_audio.wav"
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer = self.frames_per_buffer)
        self.audio_frames = []


    # Audio starts being recorded
    def record(self):
        
        self.stream.start_stream()
        while(self.open == True):
            data = self.stream.read(self.frames_per_buffer) 
            self.audio_frames.append(data)
            if self.open==False:
                break
        
            
    # Finishes the audio recording therefore the thread too    
    def stop(self):
       
        if self.open==True:
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
               
            waveFile = wave.open(self.audio_filename, 'wb')
            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(self.audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)
            waveFile.writeframes(b''.join(self.audio_frames))
            waveFile.close()
        
        pass
    
    # Launches the audio recording function using a thread
    def start(self):
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()

def start_AVrecording(filename):
				
	global video_thread
	global audio_thread
	
	video_thread = VideoRecorder()
	audio_thread = AudioRecorder()

	audio_thread.start()
	video_thread.start()

	return filename

def start_video_recording(filename):
				
	global video_thread
	
	video_thread = VideoRecorder()
	video_thread.start()

	return filename
	
def start_audio_recording(filename):
				
	global audio_thread
	
	audio_thread = AudioRecorder()
	audio_thread.start()

	return filename

def stop_AVrecording(filename):
	
	audio_thread.stop() 
	frame_counts = video_thread.frame_counts
	elapsed_time = time.time() - video_thread.start_time
	recorded_fps = frame_counts / elapsed_time
	print( "total frames " + str(frame_counts))
	print( "elapsed time " + str(elapsed_time))
	print( "recorded fps " + str(recorded_fps))
	video_thread.stop() 

	# Makes sure the threads have finished
	while threading.active_count() > 1:
		time.sleep(1)

	
#	 Merging audio and video signal
	
	if abs(recorded_fps - 6) >= 0.01:    # If the fps rate was higher/lower than expected, re-encode it to the expected
										
		print( "Re-encoding")
		cmd = "ffmpeg -r " + str(recorded_fps) + " -i temp_video.avi -pix_fmt yuv420p -r 6 temp_video2.avi"
		subprocess.call(cmd, shell=True)
	
		print( "Muxing")
		cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video2.avi -pix_fmt yuv420p " + filename + ".avi"
		subprocess.call(cmd, shell=True)
	
	else:
		
		print( "Normal recording\nMuxing")
		cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video.avi -pix_fmt yuv420p " + filename + ".avi"
		subprocess.call(cmd, shell=True)

		print( "..")

# Required and wanted processing of final files
def file_manager(filename):

	local_path = os.getcwd()

	if os.path.exists(str(local_path) + "/temp_audio.wav"):
		os.remove(str(local_path) + "/temp_audio.wav")
	
	if os.path.exists(str(local_path) + "/temp_video.avi"):
		os.remove(str(local_path) + "/temp_video.avi")

	if os.path.exists(str(local_path) + "/temp_video2.avi"):
		os.remove(str(local_path) + "/temp_video2.avi")

	while os.path.exists(str(local_path) + "/" + filename + ".avi"):
		filename += "+"

	return filename
	
	
if __name__== "__main__":
	
	filename = "Default_user"	
	filename = file_manager(filename)
	
	print(filename)
	print()
	print()
	print()
	print()
	print()
	print()
	print()
	print()
	print()
	print()
	print()
	print()
	
	start_AVrecording(filename)  
	
	time.sleep(10)
	
	stop_AVrecording(filename)
	print( "Done")

