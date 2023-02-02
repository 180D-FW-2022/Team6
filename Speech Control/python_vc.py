import speech_recognition as sr
import threading
import time
import os

# function for response to command
command = "m"

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

def respond():
    global command

    while(True):
        if "start" in command:
            print("Start Recording")

        if "stop" in command:
            print("Stop Recording")

        if "calibrate" in command:
            print("Calibrating")

if __name__ == '__main__':
    t1 = threading.Thread(target=hear)
    t2 = threading.Thread(target=respond)

    t1.start()
    t2.start()

    t1.join()
    t2.join()