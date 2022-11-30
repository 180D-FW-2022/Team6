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

# create socket
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '131.179.29.237' # paste your server ip address here
port = 9999
client_socket.connect((host_ip,port)) # a tuple
data = b""
payload_size = struct.calcsize("Q")


# From Speech recognition code

command = "m"

def respond():
	global command
	global cap, ret, frame
	global begin
	begin = False
	print(begin)
	while(begin == False):
		print(begin)
		time.sleep(1)
		try:
			frame_width = int(cap.get(3))
			frame_height = int(cap.get(4))

			size = (frame_width, frame_height)

			# 275 is a frame rate that I have decided looks the closest to real speed
			result = cv2.VideoWriter(r'C:\Users\mrmab\OneDrive\Documents\GitHub\Team6\Speech Control\001.avi',cv2.VideoWriter_fourcc(*'MJPG'),275,size)

			print("Camera on")
			begin = True

		except:
			print("Camera not ready")

	while True:
		while True:
			if "start" in command.lower():
				print("Start Recording")		
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
						print("Stop Recording")
						break
					
					# Show the final output
					cv2.imshow("Output", frame)

					######################################################################################################

					#################################### Speech Recognition ###################################
					result.write(frame)
					if "stop" in command.lower():
						print("Stop Recording")
						cap.release()
						cv2.destroyAllWindows()
						break
					###########################################################################################
					
					if cv2.waitKey(1) == ord('q'):
						break
					if cv2.waitKey(1) & 0xFF == 27:
						break
			if "stop" in command:
				break
			if "exit" in command:
				exit()

		# When everything done, release the capture
		result.release()
		cap.release()
		cv2.destroyAllWindows()
############################################ Speech Recognition #############################################	
# function to translate audio to command

def hear():
    global begin
    time.sleep(5)
    
    while(True):
        
        global command

        r = sr.Recognizer()
        with sr.Microphone() as source:
            while(begin == False):
                time.sleep(0.5)

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