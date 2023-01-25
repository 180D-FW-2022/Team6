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
# print(classNames)
##########################################################################################


# create socket
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# client_tracking_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '169.232.126.22' # paste your server ip address here
port = 9999
# tracking_port = 9998
client_socket.connect((host_ip,port)) # a tuple
# client_tracking_socket.connect((host_ip,tracking_port))
data = b""
payload_size = struct.calcsize("Q")


# From Speech recognition code

command = "m"

def frompi():
	global command
	global data
	##################### Face Tracking Code #################
	haar_xml = pkg_resources.resource_filename('cv2', 'data/haarcascade_frontalface_default.xml')
	faceCascade = cv2.CascadeClassifier('../Tracking/Haarcascades/haarcascade_frontalface_default.xml')

	# font 
	font = cv2.FONT_HERSHEY_SIMPLEX  
	# org 
	org = (50, 50)   
	# fontScale 
	fontScale = 1   
	# Blue color in BGR 
	color = (255, 0, 0)   
	# Line thickness of 2 px 
	thickness = 2

	# ========================================================================
	sync_freq = 0 
	# ========================================================================

	# Initial info
	max_PAN      = 180
	max_TILT     = 145
	min_PAN      = 0
	min_TILT     = 0

	max_rate_TILT = 3
	max_rate_PAN  = 3
		
	step_PAN     = 1
	step_TILT    = 1
	current_PAN  = 90
	current_TILT = 60


	# pseudo-PID control
	k_PAN = 0.015
	k_TILT = -0.015

	kd_PAN = 0.095
	kd_TILT = -0.095

	error_acceptance = 15
	# ========================================================================
	previous_x = 0
	previous_y = 0

	previous_h = 0
	previous_w = 0                  

	delta_x = 0
	delta_y = 0

	previous_delta_x = 0
	previous_delta_y = 0

	delta_x_dot = 0
	delta_y_dot = 0

	rectangle_found = 0
	# vid = cv2.VideoCapture(0)
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
		# Try to reduce lagging issues
		if sync_freq == 0:
			# Capture frame-by-frame
			# ret, frame = vid.read()
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			faces = faceCascade.detectMultiScale(gray,scaleFactor=1.2, minNeighbors=4, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
			
		if sync_freq < 0:
			sync_freq += 1
			# stopping blinking rectangle
#             if rectangle_found > 0:
#                 cv2.rectangle(frame, (previous_x, previous_y), (x+previous_w, y+previous_h), (0, 255, 0), 2)            
		#
		else:            
			sync_freq = 0
			rectangle_found = 0
			for (x, y, w, h) in faces:
				cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
				rectangle_found += 1
				if rectangle_found == 1:                    
					# print(' x y previous ', previous_x, previous_y)                    
# ========================================================================================
					# stay away from me !
#                     delta_x = previous_x - x
#                     delta_y = previous_y - y

					# get in touch !                   
					
					delta_x = 300 - x
					delta_y = 200 - y
					
					
					delta_x_dot = delta_x - previous_delta_x
					delta_y_dot = delta_y - previous_delta_y
					
# ========================================================================================
					# ignoring small error
					if abs(delta_x) < error_acceptance:
						delta_x     = 0
						delta_x_dot = 0
						
					if abs(delta_y) < error_acceptance:
						delta_y     = 0
						delta_y_dot = 0
# ========================================================================================
					# print(' x y new ', x, y)
					
					previous_x = x
					previous_y = y
					
					previous_h = h
					previous_w = w
					
					previous_delta_x = delta_x
					previous_delta_y = delta_y
					
					cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
					cv2.putText(frame, str(x) + " " + str(y), (x, y), font, fontScale, (75, 75, 0), thickness, cv2.LINE_AA)
		
		if rectangle_found > 0 and (abs(delta_x) < 500 and abs(delta_y) < 500):
			# stay away
#             k_PAN = -0.01
#             k_TILT = +0.01
			# get in touch            
			# print('pan tilt -- current ', current_PAN, current_TILT)

			# pseu-do PID
			delta_TILT = k_TILT * delta_y + kd_TILT * delta_y_dot
			# rate-limiter
			delta_TILT = min(abs(delta_TILT), max_rate_TILT)*numpy.sign(delta_TILT)
			# noise exclude
			if abs(delta_TILT) < step_TILT:
				delta_TILT = 0
			# here we go
			current_TILT = current_TILT + delta_TILT

			
			if current_TILT > max_TILT:
				current_TILT = max_TILT                
			if current_TILT < min_TILT:                
				current_TILT = min_TILT
				
			# print('delta tilt ', delta_TILT)
			# pseu-do PID
			delta_PAN = k_PAN * delta_x + kd_PAN * delta_x_dot
			# rate-limiter
			delta_PAN = min(abs(delta_PAN), max_rate_PAN)*numpy.sign(delta_PAN)
			# noise exclude
			if abs(delta_PAN) < step_PAN:
				delta_PAN = 0            
			# here we go
			
			current_PAN = current_PAN + delta_PAN
				
			if current_PAN > max_PAN:
				current_PAN = max_PAN                
			if current_PAN < min_PAN:                
				current_PAN = min_PAN           
			
			# print('delta PAN ', delta_PAN)
			
			# print('delta_x delta_y ', delta_x, delta_y)
			
			# print('pan tilt -- new ', current_PAN, current_TILT)            
			
			# pwm.setRotationAngle(1, current_PAN)
			# pwm.setRotationAngle(0, current_TILT)
			# pan_tilt_update_string = str(current_PAN) + ',' + str(current_TILT) + "\n"
			pan_tilt_update_string = "test"
			print(pan_tilt_update_string.encode())
			# print(client_tracking_socket.sendall(pan_tilt_update_string.encode()))
			# sys.stdout = sys.__stdout__
			# print(pan_tilt_update_string)
			# sys.stdout = open(os.devnull, 'w')

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