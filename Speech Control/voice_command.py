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

def camera():
    global cap, ret, frame
    while(True):
        cap = cv2.VideoCapture(0)
        while(True):
            ret, frame = cap.read()
            #cv2.imshow('frame',frame)
            if cv2.waitKey(5) & 0xFF == 27:
                break
        cap.release()
        cv2.destroyAllWindows()


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
            result = cv2.VideoWriter(r'C:\Users\ovadi\OneDrive\Documents\GitHub\Team6\Speech Control\001.avi',cv2.VideoWriter_fourcc(*'MJPG'),275,size)

            print("Camera on")
            begin = True

        except:
            print("Camera not ready")


    while(True):
        while(True):
            if "start" in command:
                print("Start Recording")
                while(True):
                    result.write(frame)

                    if "stop" in command:
                        print("Stop Recording")
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
    t2 = threading.Thread(target=camera)
    t3 = threading.Thread(target=respond)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
            
