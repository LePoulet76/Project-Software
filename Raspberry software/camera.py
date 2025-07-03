import cv2
import numpy as np
from picamera2 import Picamera2
import time
import subprocess

# functions to control the display power
def ecran_on():
    subprocess.run(['vcgencmd', 'display_power', '1'])

def ecran_off():
    subprocess.run(['vcgencmd', 'display_power', '0'])

# variables
last_movement = time.time()
timeout = 30  # seconds before turning off the screen
# initial state of the screen
ecran_est_on = False

# initialize the camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()
time.sleep(2)

# capture the first frame
frame1 = picam2.capture_array()
gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)

print("Start supervising for movement...")

# main loop
while True:
    frame2 = picam2.capture_array()
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)

    delta = cv2.absdiff(gray1, gray2)
    thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    movement = False
    for c in contours:
        # parameterize the contour
        if cv2.contourArea(c) > 3000:
            movement = True

    # if movement detected
    if movement:
        last_movement = time.time()
        if not ecran_est_on:
            print("Mouvement detected, turning on the screen.")
            # turn on the screen
            ecran_on()
            ecran_est_on = True

    # if no movement detected for a while : timeout
    if ecran_est_on and (time.time() - last_movement > timeout):
        print("Turn off the screen due to inactivity.")
        # turn off the screen
        ecran_off()
        ecran_est_on = False

    gray1 = gray2
    time.sleep(0.2)

