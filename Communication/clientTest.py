#Source: https://pyshine.com/Socket-programming-and-openc/
#Future UDP Possibility: https://pyshine.com/Server-sends-UDP-video-and-client-saves/
#Possible threading and fps improvement on pi: https://pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
# lets make the client code
import socket,cv2, pickle,struct

# create socket
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '131.179.43.13' # paste your server ip address here
port = 9999
client_socket.connect((host_ip,port)) # a tuple
data = b""
payload_size = struct.calcsize("Q")
while True:
	while len(data) < payload_size:
		packet = client_socket.recv(4*1024) # 4K
		if not packet: break
		data+=packet
	packed_msg_size = data[:payload_size] #determine how much of the packet is frame data
	data = data[payload_size:] #data now only contains frame data
	# print(packed_msg_size)
	msg_size = struct.unpack("Q",packed_msg_size)[0]
	
	while len(data) < msg_size: #Keep receiving data until the entire packet is received. We know how much to expect based on the message size
		data += client_socket.recv(4*1024)
	frame_data = data[:msg_size]
	data  = data[msg_size:]
	frame = pickle.loads(frame_data)
	cv2.imshow("RECEIVING VIDEO",frame)
	key = cv2.waitKey(1) & 0xFF
	if key  == ord('q'):
		break
client_socket.close()