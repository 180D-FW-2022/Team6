#Source: https://pyshine.com/Socket-programming-and-openc/
# Communication Dependencies
import socket,cv2,pickle,struct

# Speech Recognition Dependencies
import speech_recognition as sr
import threading
import time
import wave
import sys, os
import subprocess

# Face Tracking Dependencies
import pkg_resources
import keyboard

# Gesture Recognition Dependencies
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model

# Import IPs
import userUI

# Create sockets for communication
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_tracking_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_audio_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#remote_speech_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#remote_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

videographer_ip = userUI.videographer_ip # paste your server ip address here
remote_ip = userUI.remote_ip

videographer_port = 9999
tracking_port = 9998
client_audio_port = 9997

remote_port = 9999
remote_speech_port = 9998


client_socket.connect((videographer_ip,videographer_port))
client_tracking_socket.connect((videographer_ip,tracking_port))
client_audio_socket.connect((videographer_ip,client_audio_port))
#remote_speech_socket.connect((remote_ip,remote_speech_port))
#remote_socket.connect((remote_ip,remote_port))

#remote_socket.setblocking(0)
#remote_speech_socket.setblocking(0)
client_audio_socket.setblocking(0)

data = b""
audio_data = b""
payload_size = struct.calcsize("Q")

# initialize mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Load the gesture recognizer model
model = load_model('mp_hand_gesture')

# Load class names
f = open('gesture.names', 'r')
classNames = f.read().split('\n')
f.close()
direction = b''
##########################################################################################
fps = 5.6               # fps should be the minimum constant rate at which the camera can
fourcc = "MJPG"       # capture images (with no decrease in speed over time; testing is required)
frameSize = (320,240) # video formats and sizes also depend and vary according to the camera used
video_writer = cv2.VideoWriter_fourcc(*fourcc)
video_out = cv2.VideoWriter("temp_video.avi", video_writer, fps, frameSize)
audio_frame_count = 0
audio_frames = []

# From Speech recognition code
command = "m"

def frompi():
	global command
	global data
	global direction
	global video_out
	global video_writer
	global frameSize
	global fourcc
	global fps
	global audio_frame_count
	global audio_data
	global audio_frames
	# Set the initial position of the motor
	initial_position = 0
	desired_face_area = 0
	current_face_area = 0
	calledCallibrate = False
	callibrated = False
	moving = False

	manual_control = True
	min_detection_confidence=0.5

	##################### Face Tracking Code #################
	haar_xml = pkg_resources.resource_filename('cv2', 'data/haarcascade_frontalface_default.xml')
	face_cascade = cv2.CascadeClassifier('../Tracking/Haarcascades/haarcascade_frontalface_default.xml')

	# vid = cv2.VideoCapture(0)
	last_message_time = time.time()
	start_time = time.time()
	###########################################################
	if manual_control:
		print("IMU Control")
	else:
		print("Face Tracking")
	stopped = False
	while True:
		current_time = time.time()
		if current_time - start_time > userUI.video_length *2 and not stopped:
			# local_path = os.getcwd()
			filename = userUI.filename
			# if os.path.exists(str(local_path) + "/temp_audio.wav"):
			# 	os.remove(str(local_path) + "/temp_audio.wav")
			
			# if os.path.exists(str(local_path) + "/temp_video.avi"):
			# 	os.remove(str(local_path) + "/temp_video.avi")

			# if os.path.exists(str(local_path) + "/temp_video2.avi"):
			# 	os.remove(str(local_path) + "/temp_video2.avi")

			# while os.path.exists(str(local_path) + "/" + filename + ".avi"):
			# 	filename += "+"

			recorded_fps = audio_frame_count / (current_time - start_time)

			video_out.release()
			waveFile = wave.open(userUI.audio_filename, 'wb')
			waveFile.setnchannels(userUI.channels)
			waveFile.setsampwidth(2)
			waveFile.setframerate(2000)
			waveFile.writeframes(b''.join(audio_frames))
			waveFile.close()
			
			print("Stopped")
			print(audio_frame_count)
			print(current_time - start_time)
			print(len(audio_frames))
			stopped = True

			
			
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

		##### Camera Frame Handler ######
		while len(data) < payload_size:
			packet = client_socket.recv(4*1024) # 4K
			if not packet: break
			data+=packet

		packed_msg_size = data[:payload_size]
		data = data[payload_size:]

		msg_size = struct.unpack("Q",packed_msg_size)[0]
		
		while len(data) < msg_size:
			data += client_socket.recv(4*1024)
		frame_data = data[:msg_size]
		data  = data[msg_size:]

		try:
			frame = pickle.loads(frame_data)
			video_out.write(frame)
			audio_frame_count += 1
			time.sleep(0.16)
		except:
			print('camera error')
			continue
		###################################

		##### Audio Frame Handler ######
		try:
			# print("audio 1")
			while len(audio_data) < payload_size:
				audio_packet = client_audio_socket.recv(4*1024) # 4K
				if not audio_packet: break
				audio_data +=audio_packet
			# print("audio 2")
			audio_packed_msg_size = audio_data[:payload_size]
			audio_data = audio_data[payload_size:]

			audio_msg_size = struct.unpack("Q",audio_packed_msg_size)[0]
			# print("audio 3")
			while len(audio_data) < audio_msg_size:
				audio_data += client_audio_socket.recv(4*1024)
				# print("1st")
			# print("tasdasfd")
			audio_frame_data = audio_data[:audio_msg_size]
			# print("asdfa")
			audio_data  = audio_data[audio_msg_size:]
			# print("audio 4")
			audio_frame = pickle.loads(audio_frame_data)
			# print("success")

			audio_frames.append(audio_frame)
			
			time.sleep(0.16)
		except:
			pass
		###################################

		# img,frame = vid.read()
		
		# cv2.imshow("RECEIVING VIDEO",frame)
		
		sys.stdout = open(os.devnull, 'w')

		################################ Gesture Recognition Code #########################################
		
		x, y, c = frame.shape

		# Flip the frame vertically
		frame = cv2.flip(frame, 1)
		framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		# Get hand landmark prediction
		result = hands.process(framergb)

		# print(result)
		className = ''

		# post process the result
		if result.multi_hand_landmarks:
			landmarks = []
			for handslms in result.multi_hand_landmarks:
				for lm in handslms.landmark:
					# print(id, lm)
					lmx = int(lm.x * x)
					lmy = int(lm.y * y)
					
					landmarks.append([lmx, lmy])

				# Drawing landmarks on frames
				mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)

				# Predict gesture
				prediction = model.predict([landmarks])
				classID = np.argmax(prediction)
				# Only print prediction if its "stop", "okay", or "rock"
				if prediction[0][classID] > min_detection_confidence and classNames[classID] in ["stop","okay","rock"]:
					className = classNames[classID]

		# show the prediction on the frame
		cv2.putText(frame, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,1, (0,0,255), 2, cv2.LINE_AA)
		
		# Stop if the stop gesture is recognized

		# if "stop" in className.lower():
		# 	print("stop camera")
		# 	cap.release()
		# 	cv2.destroyAllWindows()
		# 	break
		
		if "rock" in className.lower():
			if not manual_control:
				# sys.stdout = sys.__stdout__ 
				print("IMU Control")
				# sys.stdout = open(os.devnull, 'w')
				manual_control = True

		if "okay" in className.lower():
			if manual_control:
				# sys.stdout = sys.__stdout__ 
				print("Face Tracking")
				# sys.stdout = open(os.devnull, 'w')
				manual_control = False
		

		############################### End of Gesture Recognition Code ###########################
		sys.stdout = sys.__stdout__ 

		#################################### Speech Recognition ###################################
		# if "stop" in command.lower():
		# 	print("stop camera")
		# 	# cap.release()
		# 	cv2.destroyAllWindows()
		# 	break
		
		###########################################################################################
			
		
		if not manual_control:
			################################################## Face Tracking Code #################################################
			# Convert the frame to grayscale
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

			faces = face_cascade.detectMultiScale(gray,scaleFactor=1.2, minNeighbors=4, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

			areas=[]
			if np.any(faces): # faces is not empty
				# find the largest face 
				if (len(faces)>1): # if there are more than one face
					for (x, y, w, h) in faces:
						areas.append((x+w)*(y+h))

					maxArea = max(areas)
					maxAreaPos = areas.index(maxArea)

					face = faces[maxAreaPos] #largest face
				elif (len(faces)==1):
					face = faces[0]
			
				(x,y,w,h) = face 

				# Draw a rectangle around the faces
				cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

				# Get the center of the face
				face_center_x = x + w/2
				face_center_y = y + h/2
				
				# field of view center
				frame_center_x = frame.shape[1]/2
				frame_center_y = frame.shape[0]/2

				# calculate the area of the desired face rectangle
				current_area = (x+w)*(y+h)
				
				# Calculate the error from the center of the frame
				error_x = frame_center_x - face_center_x
				error_y = frame_center_y - face_center_y
				
				# print("error_x")
				# print(error_x)
				
				sys.stdout = sys.__stdout__	
				# left and right motion
				if (error_x>70): #TODO: include tolerances
					direction = b"RIGHTFT\n"
					if current_time - last_message_time > 1.5:
						client_tracking_socket.sendall(direction)
						# print(direction)
					moving = True
					# continue
				elif (error_x<-70):
					#todo: directions might be wrong
					direction = b"LEFTFT\n"
					if current_time - last_message_time > 1.5:
						client_tracking_socket.sendall(direction)
						# print(direction)
					moving = True
					# continue
				else:
					moving = False
				
				# callibrate
				if "calibrate" in command.lower() and not calledCallibrate:
					sys.stdout = sys.__stdout__ 
					desired_face_area = current_area
					callibrated = True
					print("calibrate confirmed")
					calledCallibrate = True
					# sys.stdout = open(os.devnull, 'w')


				if callibrated:
					if (current_area - desired_face_area >150): #TODO: can change the tolerance
						direction = b"BACKFT\n"
						if current_time - last_message_time > 1.5:
							client_tracking_socket.sendall(direction)
							# print(direction)
						moving = True
					elif (current_area - desired_face_area<-150):
						direction = b"FRONTFT\n"
						if current_time - last_message_time > 1.5:
							client_tracking_socket.sendall(direction)
							# print(direction)
						moving = True
					else:
						moving = False
				# else:
				# 	print ("not callibrated")
				
				if current_time - last_message_time > 1.5:
					last_message_time = current_time
				
				if not moving:
					direction = b"STOP\n"
					client_tracking_socket.sendall(direction)
					# print(direction)
			else: #faces empty
				# sys.stdout = open(os.devnull, 'w')
				print("faces empty")
				direction = b"STOP\n"
				client_tracking_socket.sendall(direction)
				# print(direction)
			
			
			# print(direction)
			# sys.stdout = open(os.devnull, 'w')

			

			if cv2.waitKey(1) == ord('q'):
				break
		
		if manual_control:
			try:
				from_IMU = ''
				#from_IMU = remote_socket.recv(4096)
				# sys.stdout = sys.__stdout__ 
				# print(from_IMU)
				# sys.stdout = open(os.devnull, 'w')
				if from_IMU:
					client_tracking_socket.sendall(from_IMU)
			except:
				pass
		# else:
		# 	print("Car control error: Neither Manual nor Face Tracking Control")
		
		# Speech commands from remote
		# try:
		# 	speech_command = ''
		# 	speech_command = remote_speech_socket.recv(4096)
		# 	sys.stdout = sys.__stdout__ 
		# 	print(speech_command)
		# 	command = speech_command
		# 	sys.stdout = open(os.devnull, 'w')
		# except:
		# 	pass
		
		# Show the final output
		cv2.imshow("Output", frame)

		if cv2.waitKey(1) == ord('q'):
				break
		# if cv2.waitKey(1) & 0xFF == ord('r'):
		# 	manual_control =  not manual_control


############################################ Speech Recognition #############################################	
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


#         time.sleep(3)

if __name__ == '__main__':
	#frompi()

	t1 = threading.Thread(target=hear)
	t2 = threading.Thread(target=frompi)

	t1.start()
	t2.start()

	t1.join()
	t2.join()
