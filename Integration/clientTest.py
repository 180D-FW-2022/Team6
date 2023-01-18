#Source: https://pyshine.com/Socket-programming-and-openc/
# lets make the client code
import socket,cv2, pickle,struct

######################### Speech Recognition Dependencies ##################################
import speech_recognition as sr
import threading
import time
import os
############################################################################################

###################### Additional Gesture Recognition Dependencies and Setup Code ####################
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model

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
# print(classNames)
##########################################################################################

###########################################################
# create socket
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '131.179.29.237' # paste your server ip address here
port = 9999
client_socket.connect((host_ip,port)) # a tuple
data = b""
payload_size = struct.calcsize("Q")


# From Speech recognition code

command = "m"

def frompi():
	global command
	global data
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
		
		if "stop" in className.lower():
			print("stop camera")
			cap.release()
			cv2.destroyAllWindows()
			break
		
		# Show the final output

		cv2.imshow("Output", frame)

		######################################################################################################

		#################################### Speech Recognition ###################################
		if "stop" in command.lower():
			print("stop camera")
			cap.release()
			cv2.destroyAllWindows()
			break
		###########################################################################################
		
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

client_socket.close()