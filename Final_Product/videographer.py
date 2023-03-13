#Source: https://pyshine.com/Socket-programming-and-openc/

# Import the libraries
import socket, cv2, pickle, struct, imutils, threading
import numpy as np
import serial
import cv2
import userUI

frame = None
ret = None
vs = None

def camera_capture():
	global frame
	global ret
	global vs

	vs = cv2.VideoCapture(0)
	while(True):
		ret, frame = vs.read()

def frame_transmission():
	global frame
	global ret
	global vs
	########## Socket Setup ##########
	# Create socket
	camera_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	instruction_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	# Avoid "socket in use" error. Allows program to be run back to back
	camera_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	instruction_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	camera_port = 9999
	instruction_port = 9998

	camera_address = (userUI.videographer_ip,camera_port)
	instruction_address = (userUI.videographer_ip,instruction_port)

	# Socket Bind
	camera_socket.bind(camera_address)
	instruction_socket.bind(instruction_address)

	# Socket Listen
	camera_socket.listen(5)
	instruction_socket.listen(5)
	print("LISTENING AT:",camera_address)
	print("LISTENING AT:",instruction_address)

	# Configure serial communication to videographer
	# ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
	# ser.reset_input_buffer()

	try:
		# Socket Accept
		while True:
			laptop_camera_socket,camera_addr = camera_socket.accept()
			laptop_instruction_socket,instruction_addr = instruction_socket.accept()
			print('GOT CONNECTION FROM:',camera_addr)
			print('GOT CONNECTION FROM:',instruction_addr)
			if laptop_camera_socket and laptop_instruction_socket:
				laptop_instruction_socket.setblocking(0)
				# laptop_camera_socket.setblocking(0)
				while(vs):
					try:
						direction = laptop_instruction_socket.recv(4096)
						if direction:
							# ser.write(direction)
							pass
					except:
						pass

					#### Camera frame capture and transmission ####
					if( np.shape(frame)==()):
						continue
					if ret != True:
						continue
					frame = imutils.resize(frame,width=320,inter=cv2.INTER_LANCZOS4)
					a = pickle.dumps(frame)
					message = struct.pack("Q",len(a))+a
					try:
						laptop_camera_socket.sendall(message)
					except:
						pass
										
	finally:
		vs.release()
		cv2.destroyAllWindows()
		camera_socket.close()

if __name__ == '__main__':
	t1 = threading.Thread(target=camera_capture)
	t2 = threading.Thread(target=frame_transmission)

	t1.start()
	t2.start()

	t1.join()
	t2.join()