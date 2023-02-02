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

###################### Additional Gesture Recognition Dependencies and Setup Code ####################
import cv2
import numpy as np
import numpy
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model

sys.stdout = open(os.devnull, 'w')
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
host_ip = '131.179.29.20' # paste your server ip address here
port = 9999
tracking_port = 9998
client_socket.connect((host_ip,port)) # a tuple
client_tracking_socket.connect((host_ip,tracking_port))
data = b""
payload_size = struct.calcsize("Q")

# Set the initial position of the motor
initial_position = 0

desired_face_area = 0
current_face_area = 0
callibrated = False
moving = False

# From Speech recognition code

command = "m"

def frompi():
	global command
	global data
	##################### Face Tracking Code #################
	haar_xml = pkg_resources.resource_filename('cv2', 'data/haarcascade_frontalface_default.xml')
	faceCascade = cv2.CascadeClassifier('../Tracking/Haarcascades/haarcascade_frontalface_default.xml')

	
	###########################################################
	while True:
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
				# print(prediction)
				classID = np.argmax(prediction)
				className = classNames[classID]

		# show the prediction on the frame
		cv2.putText(frame, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,1, (0,0,255), 2, cv2.LINE_AA)
		
		# Stop if the stop gesture is recognized

		# if "stop" in className.lower():
		# 	print("stop camera")
		# 	cap.release()
		# 	cv2.destroyAllWindows()
		# 	break
		
		

		######################################################################################################

		#################################### Speech Recognition ###################################
		if "stop" in command.lower():
			print("stop camera")
			cap.release()
			cv2.destroyAllWindows()
			break
		###########################################################################################
		
		################################################## Pan-Tilt Tracking Code #################################################
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
			
			print("error_x")
			print(error_x)
			
			# left and right motion
			if (error_x>60): #TODO: include tolerances
				# ser.write(b"LEFT\n") 
				direction = b"LEFT\n"
				moving = True
			elif (error_x<-60):
				# ser.write(b"RIGHT\n") #todo: directions might be wrong
				direction = b"RIGHT\n"
				moving = True
			else:
				moving = False
			
			# callibrate
			#Delete later
			if not callibrated: #cv2.waitKey(1) & 0xFF == ord('b'):
				desired_face_area = current_area
				callibrated = True
				
			print("desired_face_area")
			print(desired_face_area)

			print("current_face_area")
			print(current_area)
			
			if callibrated:
				if (current_area - desired_face_area > 100000): #TODO: can change the tolerance
					# ser.write(b"BACK\n")
					direction = b"BACK\n"
					moving = True
				elif (current_area - desired_face_area<-100000):
					# ser.write(b"FRONT\n")
					direction = b"FRONT\n"
					moving = True
				else:
					moving = False
			else:
				print ("not callibrated")
			
			if not moving:
				# ser.write(b"STOP\n")
				direction = b"STOP\n"

		else: #faces empty
			print("faces empty")

		
		print(direction.encode())
		print(client_tracking_socket.sendall(direction.encode()))

		# Show the final output
		cv2.imshow("Output", frame)

		if cv2.waitKey(1) == ord('q'):
			break

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