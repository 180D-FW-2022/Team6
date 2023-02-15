#Source: https://pyshine.com/Socket-programming-and-openc/
# lets make the client code
import socket,cv2, pickle,struct

######################### Speech Recognition Dependencies ##################################
import speech_recognition as sr
import threading
import time
import sys, os
############################################################################################

##########Face Tracking Dependencies###############3
# from PCA9685 import PCA9685
import pkg_resources
import keyboard

###################### Additional Gesture Recognition Dependencies and Setup Code ####################
import cv2
import numpy as np
import numpy
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model

# sys.stdout = open(os.devnull, 'w')
# initialize mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7) #Change this later
mpDraw = mp.solutions.drawing_utils

# Load the gesture recognizer model
model = load_model('mp_hand_gesture')

# Load class names
f = open('gesture.names', 'r')
classNames = f.read().split('\n')
f.close()
direction = b''
# print(classNames)
##########################################################################################


# create socket
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_tracking_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
remote_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

host_ip = '131.179.41.94' # paste your server ip address here
remote_ip = '131.179.28.51'

port = 9999
tracking_port = 9998
remote_port = 9999

client_socket.connect((host_ip,port)) # a tuple
client_tracking_socket.connect((host_ip,tracking_port))
remote_socket.connect((remote_ip,remote_port))

# Socket for command
c_client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
c_client_tracking_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
c_remote_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

c_port = 9997
c_tracking_port = 9996
c_remote_port = 9997

c_client_socket.connect((host_ip,c_port)) # a tuple
c_client_tracking_socket.connect((host_ip,c_tracking_port))
c_remote_socket.connect((remote_ip,c_remote_port))
#################################################

data = b""
payload_size = struct.calcsize("Q")

#################################################

# From Speech recognition code

command = "m"

### Added this
commandData = b""
commandPayloadSize = struct.calcsize("Q")
###

def frompi():
	global command
	global data
	global direction
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
	# current_time = time.time()
	###########################################################
	while True:
		current_time = time.time()
		while len(data) < payload_size:
			packet = client_socket.recv(4*1024) # 4K
			if not packet: break
			data+=packet
		packed_msg_size = data[:payload_size]
		data = data[payload_size:]
		# print(packed_msg_size)
		msg_size = struct.unpack("Q",packed_msg_size)[0]
		
		while len(data) < msg_size:
			data += client_socket.recv(4*1024)
		frame_data = data[:msg_size]
		data  = data[msg_size:]
		frame = pickle.loads(frame_data)


		# img,frame = vid.read()
		cv2.imshow("RECEIVING VIDEO",frame)

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
			sys.stdout = sys.__stdout__ 
			print("IMU Control")
			sys.stdout = open(os.devnull, 'w')
			manual_control = True

		if "okay" in className.lower():
			sys.stdout = sys.__stdout__ 
			print("Face Tracking")
			sys.stdout = open(os.devnull, 'w')
			manual_control = False
		

		######################################################################################################
		sys.stdout = sys.__stdout__ 
		#################################### Speech Recognition ###################################
		if "stop" in command.lower():
			print("stop camera")
			# cap.release()
			cv2.destroyAllWindows()
			break
		if "calibrate" in command.lower() and not calledCallibrate:
			sys.stdout = sys.__stdout__ 
			desired_face_area = current_area
			callibrated = True
			print("calibrate confirmed")
			calledCallibrate = True
			sys.stdout = open(os.devnull, 'w')
		###########################################################################################
		try:  # used try so that if user pressed other than the given key error will not be shown
			if keyboard.is_pressed('r'):
				sys.stdout = sys.__stdout__ 
				manual_control = not manual_control
				if manual_control:
					print("IMU Control")
				else:
					print("Face Tracking")
				sys.stdout = open(os.devnull, 'w')
		except:
			print('error')
			

		if not manual_control:
			# print("face tracking control")
			################################################## Pan-Tilt Tracking Code #################################################
			# Convert the frame to grayscale
			# 
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
				# #Delete later
				# if cv2.waitKey(1) & 0xFF == ord('b'):
				# 	desired_face_area = current_area
				# 	callibrated = True
				
				# print("desired_face_area")
				# print(desired_face_area)

				# print("current_face_area")
				# print(current_area)
				

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
				else:
					print ("not callibrated")
				
				if current_time - last_message_time > 1.5:
					last_message_time = current_time

				if not moving:
					direction = b"STOP\n"
					client_tracking_socket.sendall(direction)
					# print(direction)
			else: #faces empty
				sys.stdout = open(os.devnull, 'w')
				print("faces empty")
				# direction = b"STOP\n"
				# client_tracking_socket.sendall(direction)
				# print(direction)
			
			
			# print(direction)
			sys.stdout = open(os.devnull, 'w')

			

			if cv2.waitKey(1) == ord('q'):
				break

		elif manual_control:
			# print("IMU control")
			try:
				from_IMU = ''
				from_IMU = remote_socket.recv(4096)
				sys.stdout = sys.__stdout__ 
				print(from_IMU)
				sys.stdout = open(os.devnull, 'w')
				# if from_IMU:
				# 	client_tracking_socket.sendall(from_IMU)
			except socket.error as e:
				print("No IMU message 2")
				# break
		else:
			print("Car control error: Neither Manual nor Face Tracking Control")

		# Show the final output
		cv2.imshow("Output", frame)

		if cv2.waitKey(1) & 0xFF == ord('r'):
			manual_control =  not manual_control


############################################ Speech Recognition #############################################

### Changed this whole function

def hear():
	global commandData
	global command
	global commandPayloadSize

	time.sleep(10)
    
	while True:
		current_time = time.time()
		while len(commandData) < commandPayloadSize:
			packet = c_client_socket.recv(4*1024) # 4K
			if not packet: break
			commandData+=packet
		packed_msg_size = commandData[:commandPayloadSize]
		commandData = commandData[commandPayloadSize:]
		# print(packed_msg_size)
		msg_size = struct.unpack("Q",packed_msg_size)[0]
		
		while len(commandData) < msg_size:
			commandData += c_client_socket.recv(4*1024)
		frame_data = commandData[:msg_size]
		commandData  = commandData[msg_size:]
		frame = pickle.loads(frame_data)
    


	time.sleep(3)

if __name__ == '__main__':
    t1 = threading.Thread(target=hear)
    t2 = threading.Thread(target=frompi)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

############################################################################################################################

# client_socket.close()