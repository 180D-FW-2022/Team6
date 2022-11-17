import socket
import base64
import cv2 as cv
import numpy as np

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('131.179.42.113', 8080))

# Object to capture the frames
cap = cv.VideoCapture(0)
if( not cap.isOpened() ):
  print("Error when reading steam_avi")

try:
 while True:
  # Read Frame
  _, frame = cap.read()
  # if cv.waitKey(1) & 0xFF == ord('q'):
  #       break
  # display frame
  # cv.imshow("Stream", frame)
  # Encoding the Frame
  _, buffer = cv.imencode('.jpg', frame)
  # Converting into encoded bytes
  jpg_as_text = base64.b64encode(buffer)
  client.sendall(jpg_as_text)
  from_server = client.recv(4096)

except:
 cap.release()
 client.close()
 print(from_server)
 print("\nNow you can restart fresh")

