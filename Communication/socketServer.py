# Reminder: This is a comment. The first line imports a default library "socket" into Python.
# You don’t install this. The second line is initialization to add TCP/IP protocol to the endpoint.
import socket
import base64
import numpy as np
import cv2 as cv
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Assigns a port for the server that listens to clients connecting to this port.
serv.bind(('131.179.42.113', 8080))
serv.listen(5)
frame = np.zeros((240, 320, 3), np.uint8)

while True:
    conn, addr = serv.accept()
    from_client = ''
    while True:
        data = conn.recv(4096)
        if not data:
            break
        from_client += data.decode('utf_8')
        # Decoding the message
        img = base64.b64decode(data)
        # converting into numpy array from buffer
        npimg = np.frombuffer(img, dtype=np.uint8)
        # Decode to Original Frame
        frame = cv.imdecode(npimg, 1)
        cv.imshow("Stream", frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
        print(from_client)
        conn.send("I am SERVER\n".encode())
    conn.close()
    print('client disconnected')
