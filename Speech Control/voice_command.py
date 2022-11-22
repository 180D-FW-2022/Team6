#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as sr
import cv2
import numpy as np
import threading
import time
import os

# function for response to command
command = "m"

# The state variable will change depending on whether recording is on or not
control = "off"
def respond():
    global command
    global control
    while(True):
        time.sleep(2)
        print("before " + control)
        if "start" in command:
            print("Start Recording")
            global cap
            cap = cv2.VideoCapture(0)
            control = "on"
            print("in start " + control)

            while(True):
                if "stop" in command:
                    print("Stop Recording")
                    cap.release()
                    cv2.destroyAllWindows()
                    time.sleep(3)
                    control = "off"
                    break
                #    break
                # Capture frame-by-frame
                ret, frame = cap.read()

                # Display the resulting frame
                cv2.imshow('frame',frame)
                if cv2.waitKey(5) & 0xFF == 27:
                    break
            # When everything done, release the capture
            print("done? " + control)
            cap.release()
            cv2.destroyAllWindows()

        #elif "stop" or "end" in command:
         #   print("Stop Recording")
                #cap.release()
                #cv2.destroyAllWindows()
          #  time.sleep(3)
        #else:
         #   print("waiting for command")
          #  time.sleep(1)

# function to translate audio to command

def hear():
    
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
        

        #print("hear")
        #time.sleep(2)

def print_command():
    global command
    print("entered")
    while(True):
        print("you ordered" + command)
        time.sleep(3)






# recognize speech using Google Speech Recognition
# try:

if __name__ == '__main__':
    t1 = threading.Thread(target=hear)
    t2 = threading.Thread(target=respond)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
            
            

        
       # p = mp.Process(target=respond,args=(command))


# except sr.UnknownValueError:
#     print("Google Speech Recognition could not understand audio")
# except sr.RequestError as e:
#     print("Could not request results from Google Speech Recognition service; {0}".format(e))
