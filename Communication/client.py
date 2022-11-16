# Source: https://medium.com/@pritam.mondal.0711/stream-live-video-from-client-to-server-using-opencv-and-paho-mqtt-674d3327e8b3
# Importing Libraries
import cv2 as cv
import paho.mqtt.client as mqtt
import base64
import time
# Raspberry PI IP address
MQTT_BROKER = 'test.mosquitto.org'
# Topic on which frame will be published
MQTT_SEND = "home/server/team6/gesture"
# Object to capture the frames
cap = cv.VideoCapture(0)

if( not cap.isOpened() ):
  print("Error when reading steam_avi")
# Phao-MQTT Clinet
client = mqtt.Client()
# Establishing Connection with the Broker
client.connect(MQTT_BROKER)

try:
 while True:
  start = time.time()
  # Read Frame
  _, frame = cap.read()
  if cv.waitKey(1) & 0xFF == ord('q'):
        break
  # display frame
  cv.imshow("Stream", frame)
  # Encoding the Frame
  _, buffer = cv.imencode('.jpg', frame)
  # Converting into encoded bytes
  jpg_as_text = base64.b64encode(buffer)
  # Publishig the Frame on the Topic home/server
  client.publish(MQTT_SEND, jpg_as_text)
  end = time.time()
  t = end - start
  fps = 1/t
  print(fps)
except:
 cap.release()
 client.disconnect()
 print("\nNow you can restart fresh")