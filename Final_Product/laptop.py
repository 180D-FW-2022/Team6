#Source: https://pyshine.com/Socket-programming-and-openc/
# Communication Dependencies
import socket,cv2,pickle,struct

# Speech Recognition Dependencies
import speech_recognition as sr
import threading
import time
import sys, os, keyboard

# Face Tracking Dependencies
import pkg_resources

# Gesture Recognition Dependencies
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model

# Import IPs
import userUI



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

# Create sockets for communication
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_tracking_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
remote_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# videographer_ip = userUI.videographer_ip
videographer_ip = "164.67.209.201"
remote_ip = userUI.remote_ip

videographer_port = 9999
tracking_port = 9998

remote_port = 9999


client_socket.connect((videographer_ip,videographer_port))
client_tracking_socket.connect((videographer_ip,tracking_port))
# remote_socket.connect((remote_ip,remote_port))

remote_socket.setblocking(0)

data = b""
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
video_out = cv2.VideoWriter(file_manager(userUI.filename) + ".avi", video_writer, fps, frameSize)
temp_frame = None

# From Speech recognition code
command = "m"

active_recording = False
end_program = False

def frompi():
	global command
	global data
	global direction
	global video_out
	global video_writer
	global frameSize
	global fourcc
	global fps
	global temp_frame
	global payload_size
	global active_recording
	global end_program
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
	face_cascade = cv2.CascadeClassifier('../Tracking/Haarcascades/haarcascade_frontalface_default.xml')

	last_message_time = time.time()
	start_time = time.time()
	###########################################################
	if manual_control:
		print("IMU Control")
	else:
		print("Face Tracking")

	stopped = False
	while True:
		try:
			frame = temp_frame
			current_time = time.time()
			try:  # used try so that if user pressed other than the given key error will not be shown
				if keyboard.is_pressed('e'):  # if key 'q' is pressed 
					print("here")
					end_program = True
			except:
				pass

			if end_program:
				break
			################################ Gesture Recognition Code #########################################
			# Temporarily block all system output
			sys.stdout = open(os.devnull, 'w')	

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
						lmx = int(lm.x * x)
						lmy = int(lm.y * y)
						
						landmarks.append([lmx, lmy])

					# Drawing landmarks on frames
					mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)

					# Predict gesture
					prediction = model.predict([landmarks])
					classID = np.argmax(prediction)
					# Only print prediction if its "okay" or "rock"
					if prediction[0][classID] > min_detection_confidence and classNames[classID] in ["okay","rock"]:
						className = classNames[classID]
					elif classNames[classID] == "stop" and prediction[0][0] > 0.01:
						className = "okay"
			# Enable system output
			sys.stdout = sys.__stdout__ 

			# show the prediction on the frame
			cv2.putText(frame, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,1, (0,0,255), 2, cv2.LINE_AA)

			if "rock" in className.lower():
				if not manual_control:
					print("IMU Control")
					manual_control = True

			if "okay" in className.lower():
				if manual_control: 
					print("Face Tracking")
					manual_control = False
			

			############################### End of Gesture Recognition Code ###########################
			

			#################################### Speech Recognition ###################################
			if "start recording" in command.lower():
				print("Recording in progress!")
				active_recording = True
				command = "m"

			if "stop recording" in command.lower():
				print("Recording stopped!")
				active_recording = False
				video_out.release()
				command = "m"
			
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
					
					# left and right motion
					if (error_x>70): #TODO: include tolerances
						direction = b"RIGHTFT\n"
						if current_time - last_message_time > 1.5:
							client_tracking_socket.sendall(direction)
						moving = True
					elif (error_x<-70):
						direction = b"LEFTFT\n"
						if current_time - last_message_time > 1.5:
							client_tracking_socket.sendall(direction)
						moving = True
					else:
						moving = False
					
					# callibrate
					if "calibrate" in command.lower() and not calledCallibrate:
						desired_face_area = current_area
						callibrated = True
						print("calibrate confirmed")
						calledCallibrate = True
						


					if callibrated:
						if (current_area - desired_face_area >150): 
							direction = b"BACKFT\n"
							if current_time - last_message_time > 1.5:
								client_tracking_socket.sendall(direction)
							moving = True
						elif (current_area - desired_face_area<-150):
							direction = b"FRONTFT\n"
							if current_time - last_message_time > 1.5:
								client_tracking_socket.sendall(direction)
							moving = True
						else:
							moving = False
					# else:
					# 	print ("not callibrated")
					
					if current_time - last_message_time > 1.5:
						last_message_time = current_time
					
					if not moving:
						if  direction != b"STOP\n":
							direction = b"STOP\n"
							client_tracking_socket.sendall(direction)
				else: #faces empty
					if  direction != b"STOP\n":
						direction = b"STOP\n"
						client_tracking_socket.sendall(direction)
				
				if cv2.waitKey(1) == ord('q'):
					break
			
			if manual_control:
				try:
					from_IMU = ''
					# from_IMU = remote_socket.recv(4096)
					if from_IMU:
						client_tracking_socket.sendall(from_IMU)
				except:
					pass
			
			# Show the final output
			cv2.imshow("Output", frame)

			if cv2.waitKey(1) == ord('q'):
				break
		except:
			continue

def frame_capture():
	global temp_frame
	global data
	global payload_size
	global video_out
	global active_recording
	global end_program
	while(True):
		if end_program:
			break
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
			temp_frame = pickle.loads(frame_data)
			if active_recording:
				video_out.write(temp_frame)
		except:
			continue
		###################################

############################################ Speech Recognition #############################################	
def hear():
    global end_program
    global command
    
    time.sleep(10)
    while(True):
	
        r = sr.Recognizer()
        if end_program:
            break
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


if __name__ == '__main__':
	t1 = threading.Thread(target=hear)
	t2 = threading.Thread(target=frompi)
	t3 = threading.Thread(target=frame_capture)

	t1.start()
	t2.start()
	t3.start()

	t1.join()
	t2.join()
	t3.join()
