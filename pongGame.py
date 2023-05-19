#DBUS_FATAL_WARNINGS=0 scrcpy --window-width 800 --window-height 360

import cv2
import numpy as np 
from PIL import Image
import mss 
from ppadb.client import Client
import threading
import time
import warnings

# Declaring variables
start = 1
ball_x, ball_y = 0, 0
paddle_x = 2145
paddle_y = 540
paddle_y_min = 156
paddle_y_max = 930
running = True
prev_ball_x = 410
prev_ball_y = 178
frameCounter = 0
directionUp = -1
directionRight = -1
xPixel = np.array([])
yPixel = np.array([])
m = -1
b = -1
end_y_point = paddle_y

# Setting up the adb
adb = Client(host='127.0.0.1', port=5037)
devices = adb.devices()
if len(devices) == 0:
    print('No device attached')
    quit()
device = devices[0]

def move_paddle():
    global paddle_y
    global end_y_point
    global start
    global paddle_y_min
    global paddle_y_max
    global paddle_x
    
    # Wait 1 second before starting 
    if start:
        time.sleep(1)
        start = 0
    
    while running:
        # Compute the paddles initial coordinates and supposed final coordinates so that the ball bounces back
        initial = int(paddle_y * (2400/800))
        initial = min(initial, paddle_y_max)
        initial = max(initial, paddle_y_min)

        to = int(end_y_point * (2400/800))
        to = min(to, paddle_y_max)
        to = max(to, paddle_y_min)

        # Use adb to swipe the screen to play
        device.shell(f'input touchscreen swipe {paddle_x} {initial} {paddle_x} {to} 50')

        # Wait a bit before re-swiping to avoid a 'double swipe'
        time.sleep(150/1000)

# Start the definition in parallel with the main code
t = threading.Thread(target=move_paddle)
t.start()


def predict_path():
    global xPixel
    global yPixel
    global directionRight
    global directionUp
    global end_y_point

    # Assign easy to understand values about the ball coordinate
    x1 = int(prev_ball_x)
    y1 = int(prev_ball_y)
    x2 = int(ball_x)
    y2 = int(ball_y)


    # Finding the direction of the ball
    # Clear coordinates if path direction is changed to find a new line of best fit
    if x1 < x2:
        # Moving Right
        if directionRight != 1:
            xPixel = np.array([])
            yPixel = np.array([])
            directionRight = 1
    
    elif x1 > x2:
        # Moving Left
        if directionRight != 0:
            xPixel = np.array([])
            yPixel = np.array([])
            directionRight = 0

    else:
        # Staying still
        directionRight = -1
    
    if y1 > y2:
        # Moving Up
        if directionUp != 1:
            xPixel = np.array([])
            yPixel = np.array([])
            directionUp = 1

    elif y1 < y2:    
        # Moving Down  
        if directionUp != 0:
            xPixel = np.array([])
            yPixel = np.array([])
            directionUp = 0

    else:
        # Staying still
        directionUp = -1


    # Save coordinates to find the line of best fit
    xPixel = np.append(xPixel, x2)
    yPixel = np.append(yPixel, y2)

    
    # Make sure the ball is in motion, avoids division by zero
    if directionRight!=-1 and directionUp!=-1:
        # If ball is moving to the right side
        if directionRight and len(xPixel)>4:
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings('error', category=np.RankWarning)
                    warnings.filterwarnings('error', category=RuntimeWarning)
                    #find line of best fit
                    m, b = np.polyfit(xPixel, yPixel, 1)
            except (np.RankWarning, RuntimeWarning) as e:
                print(f"Warning: {str(e)}, skipping")
                return
            
            # Find where the ball y-coordinate is suppose to hit on the right side
            right_y_Coordinate = int((m*715)+b)

            # If the ball y-coordinate is within the borders. Plot the path and find the left most coordinate.
            if 10 < right_y_Coordinate < 350:
                cv2.line(img, (x2,y2), (715, right_y_Coordinate), (0, 0, 255), 2)
                end_y_point = right_y_Coordinate

            # If ball y-coordinate hits the bottom border, reflect it, then plot the path and find the left most coordinate.
            elif right_y_Coordinate < 11.5:
                cv2.line(img, (x2,y2), (int((11.5-b)/m),11), (0, 0, 255), 2)
                cv2.line(img, (int((11.5-b)/m),11), (715,int((-m*715)+(2*11.5-b))), (0, 0, 255), 2)
                end_y_point = int((-m*715)+(2*11.5-b))

            # If ball y-coordinate hits the top border, reflect it, then plot the path and find the left most coordinate.
            elif right_y_Coordinate > 345:
                cv2.line(img, (x2,y2), (int((345-b)/m),345), (0, 0, 255), 2)
                cv2.line(img, (int((345-b)/m),345), (715,int((-m*715)+(2*345-b))), (0, 0, 255), 2)
                end_y_point = int((-m*715)+(2*345-b))   


sct = mss.mss()

# Main loop
while True:
    # Taking a screenshot where the app mirror is located
    scr = sct.grab({
        'left' : 66,
        'top' : 53,
        'width' : 799,
        'height' : 359 
    })
    img = np.array(scr)

    # Converting the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Locating the circle using the Hough Circle Transform
    circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,20,
                            param1=50,param2=30,minRadius=7,maxRadius=12)

    # Extracting the circle coordinates and drawing it with a green border
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # Update old coordinates every few frames
            if frameCounter == 4:
                prev_ball_x = ball_x
                prev_ball_y = ball_y
                frameCounter = 0
            else:
                frameCounter +=1

            # Update new coordinates every frame
            ball_x, ball_y = i[0],i[1]
            cv2.circle(img, (ball_x, ball_y), i[2], (0,255,0), 2)

    # Threshold the image to obtain a binary image
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

    # Find contours in the binary image
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
        if 708 < x < 711:
            paddle_y = int(y + (h/2))
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

    # call the definition to predict and draw the balls path
    predict_path()

    # Display the image to screen
    cv2.imshow('Screen Mirror', img)

    # Quit if 'q' is pressed
    if cv2.waitKey(25) & 0xff == ord('q'):
        cv2.destroyAllWindows()
        running = False
        break
        