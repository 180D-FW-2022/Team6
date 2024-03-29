#http://ozzmaker.com/
#!/usr/bin/python
#
#    This program  reads the angles from the acceleromteer, gyroscope
#    and mangnetometer on a BerryIMU connected to a Raspberry Pi.
#
#    This program includes two filters (low pass and median) to improve the
#    values returned from BerryIMU by reducing noise.
#
#    The BerryIMUv1, BerryIMUv2 and BerryIMUv3 are supported
#
#    This script is python 2.7 and 3 compatible
#
#    Feel free to do whatever you like with this code.
#    Distributed as-is; no warranty is given.
#
#    http://ozzmaker.com/

import sys
import time
import math
import IMU
import datetime

# Speech Recognition Dependencies
import speech_recognition as sr
import threading

# Communication Dependencies
import socket

# Import IPs
import userUI

import socket, os
# Communication socket set up
remote_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
remote_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#remote_speech_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#remote_speech_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

remote_ip = userUI.remote_ip

print('HOST IP:',remote_ip)
remote_port = 9999
remote_speech_port = 9998

remote_address = (remote_ip,remote_port)
remote_speech_address = (remote_ip,remote_speech_port)

remote_socket.bind(remote_address)
#remote_speech_socket.bind(remote_speech_address)

# function for response to command
command = "m"
begin = False

################### IMU Control Prep ##################################
RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070          # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40              # Complementary filter constant
MAG_LPF_FACTOR = 0.4    # Low pass filter constant magnetometer
ACC_LPF_FACTOR = 0.4    # Low pass filter constant for accelerometer
ACC_MEDIANTABLESIZE = 9         # Median filter table size for accelerometer. Higher = smoother but a longer delay
MAG_MEDIANTABLESIZE = 9         # Median filter table size for magnetometer. Higher = smoother but a longer delay



################# Compass Calibration values ############
# Use calibrateBerryIMU.py to get calibration values
# Calibrating the compass isnt mandatory, however a calibrated
# compass will result in a more accurate heading value.

magXmin =  0
magYmin =  0
magZmin =  0
magXmax =  0
magYmax =  0
magZmax =  0


'''
Here is an example:
magXmin =  -1748
magYmin =  -1025
magZmin =  -1876
magXmax =  959
magYmax =  1651
magZmax =  708
Dont use the above values, these are just an example.
'''
############### END Calibration offsets #################

# IMU variable setup
gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0
CFangleXFiltered = 0.0
CFangleYFiltered = 0.0
kalmanX = 0.0
kalmanY = 0.0
oldXMagRawValue = 0
oldYMagRawValue = 0
oldZMagRawValue = 0
oldXAccRawValue = 0
oldYAccRawValue = 0
oldZAccRawValue = 0

a = datetime.datetime.now()

#Setup the tables for the mdeian filter. Fill them all with '1' so we dont get devide by zero error
acc_medianTable1X = [1] * ACC_MEDIANTABLESIZE
acc_medianTable1Y = [1] * ACC_MEDIANTABLESIZE
acc_medianTable1Z = [1] * ACC_MEDIANTABLESIZE
acc_medianTable2X = [1] * ACC_MEDIANTABLESIZE
acc_medianTable2Y = [1] * ACC_MEDIANTABLESIZE
acc_medianTable2Z = [1] * ACC_MEDIANTABLESIZE
mag_medianTable1X = [1] * MAG_MEDIANTABLESIZE
mag_medianTable1Y = [1] * MAG_MEDIANTABLESIZE
mag_medianTable1Z = [1] * MAG_MEDIANTABLESIZE
mag_medianTable2X = [1] * MAG_MEDIANTABLESIZE
mag_medianTable2Y = [1] * MAG_MEDIANTABLESIZE
mag_medianTable2Z = [1] * MAG_MEDIANTABLESIZE

IMU.detectIMU()     #Detect if BerryIMU is connected.
if(IMU.BerryIMUversion == 99):
    print(" No BerryIMU found... exiting ")
    sys.exit()
IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass

#Kalman filter variables
Q_angle = 0.02
Q_gyro = 0.0015
R_angle = 0.005
y_bias = 0.0
x_bias = 0.0
XP_00 = 0.0
XP_01 = 0.0
XP_10 = 0.0
XP_11 = 0.0
YP_00 = 0.0
YP_01 = 0.0
YP_10 = 0.0
YP_11 = 0.0
KFangleX = 0.0
KFangleY = 0.0



def kalmanFilterY ( accAngle, gyroRate, DT):
    y=0.0
    S=0.0

    global KFangleY
    global Q_angle
    global Q_gyro
    global y_bias
    global YP_00
    global YP_01
    global YP_10
    global YP_11

    KFangleY = KFangleY + DT * (gyroRate - y_bias)

    YP_00 = YP_00 + ( - DT * (YP_10 + YP_01) + Q_angle * DT )
    YP_01 = YP_01 + ( - DT * YP_11 )
    YP_10 = YP_10 + ( - DT * YP_11 )
    YP_11 = YP_11 + ( + Q_gyro * DT )

    y = accAngle - KFangleY
    S = YP_00 + R_angle
    K_0 = YP_00 / S
    K_1 = YP_10 / S

    KFangleY = KFangleY + ( K_0 * y )
    y_bias = y_bias + ( K_1 * y )

    YP_00 = YP_00 - ( K_0 * YP_00 )
    YP_01 = YP_01 - ( K_0 * YP_01 )
    YP_10 = YP_10 - ( K_1 * YP_00 )
    YP_11 = YP_11 - ( K_1 * YP_01 )

    return KFangleY

def kalmanFilterX ( accAngle, gyroRate, DT):
    x=0.0
    S=0.0

    global KFangleX
    global Q_angle
    global Q_gyro
    global x_bias
    global XP_00
    global XP_01
    global XP_10
    global XP_11


    KFangleX = KFangleX + DT * (gyroRate - x_bias)

    XP_00 = XP_00 + ( - DT * (XP_10 + XP_01) + Q_angle * DT )
    XP_01 = XP_01 + ( - DT * XP_11 )
    XP_10 = XP_10 + ( - DT * XP_11 )
    XP_11 = XP_11 + ( + Q_gyro * DT )

    x = accAngle - KFangleX
    S = XP_00 + R_angle
    K_0 = XP_00 / S
    K_1 = XP_10 / S

    KFangleX = KFangleX + ( K_0 * x )
    x_bias = x_bias + ( K_1 * x )

    XP_00 = XP_00 - ( K_0 * XP_00 )
    XP_01 = XP_01 - ( K_0 * XP_01 )
    XP_10 = XP_10 - ( K_1 * XP_00 )
    XP_11 = XP_11 - ( K_1 * XP_01 )

    return KFangleX

# function to translate audio to command

def hear():
    global command
    global begin
    global remote_socket
    #global remote_speech_socket

    # print("here")
    while(True):
        if begin:
            remote_socket.setblocking(0)
            #remote_speech_socket.setblocking(0)
            while(True):
                # print("11111")
                r = sr.Recognizer()
                # r.dynamic_energy_threshold = False
                # r.energy_threshold = 50
                
                with sr.Microphone() as source:
                    print("Say something!")
                    # print(r.energy_threshold)
                    r.adjust_for_ambient_noise(source)
                    # print(r.energy_threshold)
                    try:
                        audio = r.listen(source, timeout=1)
                    except:
                        continue

                try:
                    command = r.recognize_google(audio)
                    print("Google Speech Recognition thinks you said " + command)

                except sr.UnknownValueError:
                    # print("ojjojojoj")
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    # print("woooooo")
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))

                # print("awooga")

def respond():
    global command
    global a
    global magXmin
    global magYmin
    global magZmin
    global magXmax
    global magYmax
    global magZmax
    global RAD_TO_DEG
    global M_PI
    global G_GAIN
    global AA
    global MAG_LPF_FACTOR
    global ACC_LPF_FACTOR
    global ACC_MEDIANTABLESIZE
    global MAG_MEDIANTABLESIZE 
    global gyroXangle
    global gyroYangle
    global gyroZangle
    global CFangleX
    global CFangleY
    global CFangleXFiltered
    global CFangleYFiltered
    global kalmanX
    global kalmanY
    global oldXMagRawValue
    global oldYMagRawValue
    global oldZMagRawValue
    global oldXAccRawValue
    global oldYAccRawValue
    global oldZAccRawValue
    global acc_medianTable1X
    global acc_medianTable1Y
    global acc_medianTable1Z
    global acc_medianTable2X
    global acc_medianTable2Y
    global acc_medianTable2Z
    global mag_medianTable1X
    global mag_medianTable1Y
    global mag_medianTable1Z
    global mag_medianTable2X
    global mag_medianTable2Y
    global mag_medianTable2Z
    global begin
    global remote_socket
    #global remote_speech_socket

    # Socket Listen
    remote_socket.listen(5)
    print("LISTENING AT:",remote_address)
    #remote_speech_socket.listen(5)
    print("LISTENING AT:",remote_speech_address)
    time.sleep(5)

    try:
        # Socket Accept
        while True:
            laptop_socket,laptop_addr = remote_socket.accept()
            print('GOT CONNECTION FROM:',laptop_addr)
            #laptop_speech_socket, laptop_speech_addr = remote_speech_socket.accept()
            #print('GOT CONNECTION FROM:',laptop_speech_addr)
            if laptop_socket:
                begin = True
                laptop_socket.setblocking(0)
                
                while True:
                    #Read the accelerometer,gyroscope and magnetometer values
                    ACCx = IMU.readACCx()
                    ACCy = IMU.readACCy()
                    ACCz = IMU.readACCz()
                    GYRx = IMU.readGYRx()
                    GYRy = IMU.readGYRy()
                    GYRz = IMU.readGYRz()
                    MAGx = IMU.readMAGx()
                    MAGy = IMU.readMAGy()
                    MAGz = IMU.readMAGz()


                    #Apply compass calibration
                    MAGx -= (magXmin + magXmax) /2
                    MAGy -= (magYmin + magYmax) /2
                    MAGz -= (magZmin + magZmax) /2


                    ##Calculate loop Period(LP). How long between Gyro Reads
                    b = datetime.datetime.now() - a
                    a = datetime.datetime.now()
                    LP = b.microseconds/(1000000*1.0)
                    outputString = "Loop Time %5.2f " % ( LP )



                    ###############################################
                    #### Apply low pass filter ####
                    ###############################################
                    MAGx =  MAGx  * MAG_LPF_FACTOR + oldXMagRawValue*(1 - MAG_LPF_FACTOR);
                    MAGy =  MAGy  * MAG_LPF_FACTOR + oldYMagRawValue*(1 - MAG_LPF_FACTOR);
                    MAGz =  MAGz  * MAG_LPF_FACTOR + oldZMagRawValue*(1 - MAG_LPF_FACTOR);
                    ACCx =  ACCx  * ACC_LPF_FACTOR + oldXAccRawValue*(1 - ACC_LPF_FACTOR);
                    ACCy =  ACCy  * ACC_LPF_FACTOR + oldYAccRawValue*(1 - ACC_LPF_FACTOR);
                    ACCz =  ACCz  * ACC_LPF_FACTOR + oldZAccRawValue*(1 - ACC_LPF_FACTOR);

                    oldXMagRawValue = MAGx
                    oldYMagRawValue = MAGy
                    oldZMagRawValue = MAGz
                    oldXAccRawValue = ACCx
                    oldYAccRawValue = ACCy
                    oldZAccRawValue = ACCz

                    #########################################
                    #### Median filter for accelerometer ####
                    #########################################
                    # cycle the table
                    for x in range (ACC_MEDIANTABLESIZE-1,0,-1 ):
                        acc_medianTable1X[x] = acc_medianTable1X[x-1]
                        acc_medianTable1Y[x] = acc_medianTable1Y[x-1]
                        acc_medianTable1Z[x] = acc_medianTable1Z[x-1]

                    # Insert the lates values
                    acc_medianTable1X[0] = ACCx
                    acc_medianTable1Y[0] = ACCy
                    acc_medianTable1Z[0] = ACCz

                    # Copy the tables
                    acc_medianTable2X = acc_medianTable1X[:]
                    acc_medianTable2Y = acc_medianTable1Y[:]
                    acc_medianTable2Z = acc_medianTable1Z[:]

                    # Sort table 2
                    acc_medianTable2X.sort()
                    acc_medianTable2Y.sort()
                    acc_medianTable2Z.sort()

                    # The middle value is the value we are interested in
                    ACCx = acc_medianTable2X[int(ACC_MEDIANTABLESIZE/2)];
                    ACCy = acc_medianTable2Y[int(ACC_MEDIANTABLESIZE/2)];
                    ACCz = acc_medianTable2Z[int(ACC_MEDIANTABLESIZE/2)];



                    #########################################
                    #### Median filter for magnetometer ####
                    #########################################
                    # cycle the table
                    for x in range (MAG_MEDIANTABLESIZE-1,0,-1 ):
                        mag_medianTable1X[x] = mag_medianTable1X[x-1]
                        mag_medianTable1Y[x] = mag_medianTable1Y[x-1]
                        mag_medianTable1Z[x] = mag_medianTable1Z[x-1]

                    # Insert the latest values
                    mag_medianTable1X[0] = MAGx
                    mag_medianTable1Y[0] = MAGy
                    mag_medianTable1Z[0] = MAGz

                    # Copy the tables
                    mag_medianTable2X = mag_medianTable1X[:]
                    mag_medianTable2Y = mag_medianTable1Y[:]
                    mag_medianTable2Z = mag_medianTable1Z[:]

                    # Sort table 2
                    mag_medianTable2X.sort()
                    mag_medianTable2Y.sort()
                    mag_medianTable2Z.sort()

                    # The middle value is the value we are interested in
                    MAGx = mag_medianTable2X[int(MAG_MEDIANTABLESIZE/2)];
                    MAGy = mag_medianTable2Y[int(MAG_MEDIANTABLESIZE/2)];
                    MAGz = mag_medianTable2Z[int(MAG_MEDIANTABLESIZE/2)];



                    #Convert Gyro raw to degrees per second
                    rate_gyr_x =  GYRx * G_GAIN
                    rate_gyr_y =  GYRy * G_GAIN
                    rate_gyr_z =  GYRz * G_GAIN


                    #Calculate the angles from the gyro.
                    gyroXangle+=rate_gyr_x*LP
                    gyroYangle+=rate_gyr_y*LP
                    gyroZangle+=rate_gyr_z*LP

                    #Convert Accelerometer values to degrees
                    AccXangle =  (math.atan2(ACCy,ACCz)*RAD_TO_DEG)
                    AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG


                    #Change the rotation value of the accelerometer to -/+ 180 and
                    #move the Y axis '0' point to up.  This makes it easier to read.
                    if AccYangle > 90:
                        AccYangle -= 270.0
                    else:
                        AccYangle += 90.0



                    #Complementary filter used to combine the accelerometer and gyro values.
                    CFangleX=AA*(CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle
                    CFangleY=AA*(CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle

                    #Kalman filter used to combine the accelerometer and gyro values.
                    kalmanY = kalmanFilterY(AccYangle, rate_gyr_y,LP)
                    kalmanX = kalmanFilterX(AccXangle, rate_gyr_x,LP)

                    #Calculate heading
                    heading = 180 * math.atan2(MAGy,MAGx)/M_PI

                    #Only have our heading between 0 and 360
                    if heading < 0:
                        heading += 360

                    ####################################################################
                    ###################Tilt compensated heading#########################
                    ####################################################################
                    #Normalize accelerometer raw values.
                    accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
                    accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)


                    #Calculate pitch and roll
                    pitch = math.asin(accXnorm)
                    roll = -math.asin(accYnorm/math.cos(pitch))


                    #Calculate the new tilt compensated values
                    #The compass and accelerometer are orientated differently on the the BerryIMUv1, v2 and v3.
                    #This needs to be taken into consideration when performing the calculations

                    #X compensation
                    if(IMU.BerryIMUversion == 1 or IMU.BerryIMUversion == 3):            #LSM9DS0 and (LSM6DSL & LIS2MDL)
                        magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
                    else:                                                                #LSM9DS1
                        magXcomp = MAGx*math.cos(pitch)-MAGz*math.sin(pitch)

                    #Y compensation
                    if(IMU.BerryIMUversion == 1 or IMU.BerryIMUversion == 3):            #LSM9DS0 and (LSM6DSL & LIS2MDL)
                        magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)
                    else:                                                                #LSM9DS1
                        magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)+MAGz*math.sin(roll)*math.cos(pitch)





                    #Calculate tilt compensated heading
                    tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI

                    if tiltCompensatedHeading < 0:
                        tiltCompensatedHeading += 360


                    ##################### END Tilt Compensation ########################


                    # if 1:                       #Change to '0' to stop showing the angles from the accelerometer
                    #     outputString += "#  ACCX Angle %5.2f ACCY Angle %5.2f  #  " % (AccXangle, AccYangle)

                    # if 1:                       #Change to '0' to stop  showing the angles from the gyro
                    #     outputString +="\t# GRYX Angle %5.2f  GYRY Angle %5.2f  GYRZ Angle %5.2f # " % (gyroXangle,gyroYangle,gyroZangle)

                    # if 1:                       #Change to '0' to stop  showing the angles from the complementary filter
                    #     outputString +="\t#  CFangleX Angle %5.2f   CFangleY Angle %5.2f  #" % (CFangleX,CFangleY)

                    # if 1:                       #Change to '0' to stop  showing the heading
                    #     outputString +="\t# HEADING %5.2f  tiltCompensatedHeading %5.2f #" % (heading,tiltCompensatedHeading)

                    # if 1:                       #Change to '0' to stop  showing the angles from the Kalman filter
                    #     outputString +="# kalmanX %5.2f   kalmanY %5.2f #" % (kalmanX,kalmanY)


                    # https://github.com/ozzmaker/BerryIMU/blob/master/python-BerryIMU-measure-G/berryIMU-measure-G.py#L36-L39
                    yG = (ACCx * 0.244)/1000
                    xG = (ACCy * 0.244)/1000
                    zG = (ACCz * 0.244)/1000
                    # outputString += "##### X = %fG  ##### Y =   %fG  ##### Z =  %fG  #####  " % ( yG, xG, zG)

                #code to detect forward, backward, left, and right tilt  
                    tiltdetection = ""
                    forwardtilt =  abs(yG)< .5 and xG > .8     
                    backwardtilt = abs(yG)< .5 and xG < -.8
                    righttilt = yG > .85 and abs(xG) < .8  
                    lefttilt = yG < -.85 and abs(xG) < .8 
                    stationary=1 #unless tilting at specific angles ouput will read stationary
                    

                    
                    if forwardtilt:
                        tiltdetection = 'IMU is tilting forward.\t'
                        laptop_socket.sendall(b"FRONT\n")
                        # print("front")
                    elif backwardtilt:
                        tiltdetection = 'IMU is tilting backward.\t'
                        laptop_socket.sendall(b"BACK\n")
                        # print("back")
                    elif righttilt:
                        tiltdetection = 'IMU is tilting right.\t'
                        laptop_socket.sendall(b"RIGHT\n")
                        # print("right")
                    elif lefttilt:
                        tiltdetection = 'IMU is tilting left.\t'
                        laptop_socket.sendall(b"LEFT\n")
                        # print("left")
                    elif stationary:
                        tiltdetection = 'IMU is stationary.\t'
                        laptop_socket.sendall(b"STOP\n")
                        # print("stop")
                    
                    
                    # print(outputString)
                    # print(tiltdetection)
                    # # slow program down a bit, makes the output more readable
                    # time.sleep(0.03)

                    # if "start" in command:
                    #     laptop_speech_socket.sendall("Start Recording")
                    #     print("Start Recording")
                    #     command = "m"

                    # if "stop" in command:
                    #     laptop_speech_socket.sendall("Stop Recording")
                    #     print("Stop Recording")
                    #     command = "m"

                    # if "calibrate" in command:
                    #     laptop_speech_socket.sendall("calibrate")
                    #     print("Calibrating")
                    #     command = "m"
    finally: 
        remote_socket.close()
        # remote_speech_socket.close()
        

if __name__ == '__main__':
    # respond()
    t1 = threading.Thread(target=hear)
    t2 = threading.Thread(target=respond)

    t1.start()
    t2.start()

    t1.join()
    t2.join()






