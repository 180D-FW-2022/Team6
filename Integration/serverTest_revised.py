#Source: https://pyshine.com/Socket-programming-and-openc/
# Welcome to PyShine

# This code is for the server 
# Lets import the libraries
import socket, cv2, pickle,struct #,imutils
import numpy as np

#################################################### Pan-Tilt Tracking Initializations ######################################################################

import numpy
import cv2
from PCA9685 import PCA9685


import pkg_resources

#setting start up serrvo positions
# ========================================================================
pwm = PCA9685()
pwm.setPWMFreq(50)

current_PAN  = 90
current_TILT = 60
pwm.setRotationAngle(1, current_PAN) #PAN    
pwm.setRotationAngle(0, current_TILT) #TILT

######################################################################### End of Pan-Tilt Tracking Initializations ####################################################################################

# Socket Create
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name  = socket.gethostname()
host_ip = '169.232.126.228' #socket.gethostbyname(host_name)
print('HOST IP:',host_ip)
port = 9999
socket_address = (host_ip,port)

# Socket Bind
server_socket.bind(socket_address)

# Socket Listen
server_socket.listen(5)
print("LISTENING AT:",socket_address)

try:
	# Socket Accept
	while True:
		client_socket,addr = server_socket.accept()
		print('GOT CONNECTION FROM:',addr)
		if client_socket:
			vid = cv2.VideoCapture(0)
			vid.release()
			vid = cv2.VideoCapture(0)
			
			while(vid.isOpened()):
				img,frame = vid.read()
				# frame = imutils.resize(frame,width=320,inter=cv2.INTER_LANCZOS4)
				a = pickle.dumps(frame)
				message = struct.pack("Q",len(a))+a
				if( np.shape(frame)==()):
					print(message)
					continue
				client_socket.sendall(message)
							
finally:
	# shut down cleanly
    pwm.exit_PCA9685()
    
    vid.release()
    #cv2.destroyAllWindows()