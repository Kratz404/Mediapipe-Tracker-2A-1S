import mediapipe as mp
import cv2

from pyfirmata import Arduino, SERVO, util
import time
import tkinter as tk

# Turret-mounted Camera

# Initialize board
board = Arduino('COM3')

current_rotation = 0

# Position 0
PT0 = 90
PT0X = 90
PT0Y = 30

LM = RM = 5 # Set x Limit, for full 180, set: LM = RM = 0
#UM = DM = 30 # Set y Limit, for full 180, set: UM = DM = 0
UM = 5
DM = 5

# Define "Far", "Close"
FarGP = 140 # Close to object, FarGP means open furthest/widest
CloseGP = 65 # Far to object
safeDistamp = 0.25

amp = 0.2 # Amplifier, default = 1, the smaller the amplifier, the finer (accuracy) it move but also slower
GPamp = 4.5

# x axis servo
pin = board.digital[3]
pin.mode = SERVO

# y axis servo
pin2 = board.digital[4]
pin2.mode = SERVO


ROIWidth = 440
ROIHeight = 380

# Switching directions
x_invert = False
y_invert = True

# Angle calibration
x_calib = 30
y_calib = 25

pin.write(PT0)
pin2.write(PT0)
    
# Sweep 180 degrees on startup
time.sleep(2)
pin.write(180)

time.sleep(0.2)
pin2.write(180)

time.sleep(1)
pin.write(0)

time.sleep(0.2)
pin2.write(0)


time.sleep(2)
pin.write(PT0)
time.sleep(0.2)
pin2.write(PT0Y)


mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

cap = cv2.VideoCapture(1)

# Initiate holistic model
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    
    while cap.isOpened():
        ret, frame = cap.read()

        # Get the height and width of the window/camera resolution
        height, width, _ = frame.shape
        
        # Get the center position of the camera
        centerPointWidth = width/2
        centerPointHeight = height/2

        color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        "This part is for Image detections / Vision"
        # Recolor Feed
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Make Detections
        result = holistic.process(image)

        # face_landmarks, pose_landmarks, left_hand_landmarks, right_hand_landmarks

        # Recolor image back to BGR for rendering
        image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Draw face landmarks
        #mp_drawing.draw_landmarks(image, result.face_landmarks, mp_holistic.FACEMESH_TESSELATION) # [FACE_CONNECTIONS] renamed to [FACEMESH_TESSELATION]

        # Right hand
        #mp_drawing.draw_landmarks(image, result.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

        # Left hand
        #mp_drawing.draw_landmarks(image, result.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

        # Pose Detections
        mp_drawing.draw_landmarks(image, result.pose_landmarks, mp_holistic.POSE_CONNECTIONS)


#--------------------------------------------------------------------------------------------------

        """Get Position Coordinates"""
        if result.pose_landmarks:
            for id, lm in enumerate(result.pose_landmarks.landmark):
                if id == 0:
                    #print(f'id: {id}')
                    #print(f'lm: {lm}')
                    #print(id, lm.x) # lm.x to get x coord, similarly with lm.y and lm.z

                    "This part is for controlling"
                    CX = width * lm.x   # center point position of the box x axis
                    CY = height * lm.y   # center point position of the box y axis

                    print("---------------------")
                    print(f"Center point width Camera: {centerPointWidth}")
                    print("\n")
                    print(f"Center point height Camera: {centerPointHeight}")
                    print("\n")
                    #print(f'lm.x : {lm.x}')
                    #print("\n")
                    #print(f'lm.y : {lm.y}')
                    #print("\n")
                    print("Target x axis: ", CX)
                    print("\n")
                    print("Target y axis: ", CY)
                    print("\n")

                    # Get new servo angle according to new center
                    distX = centerPointWidth - CX
                    #print("Distance: ", distX)
                    #print("\n")
                    
                    distY = centerPointHeight - CY
                    print("Distance: ", distY)
                    print("\n")
                
                    # Encode 180
                    encX = centerPointWidth/90
                    encY = centerPointHeight/90
                    
                    #rotX = distX/encX
                    encDistX = distX/180
                    encDistY = distY/180
                    
                    # x axis
                    if distX != 0:
                        varencdistX = encX - encDistX
                        print("varendist X: ", varencdistX)
                        
                        if encDistX > 0:
                            pin.write(PT0X+varencdistX*amp)
                            if 180-PT0X < RM:
                                PT0X = 180-RM
                            else:
                                PT0X = PT0X + varencdistX*amp
                            print(PT0X)
                            
                        if encDistX < 0:
                            pin.write(PT0X-varencdistX*amp)
                            if PT0X < LM:
                                PT0X = LM
                            else:
                                PT0X = PT0X - varencdistX*amp
                            print(PT0X)
                    
                    # y axis
                    if distY != 0:
                        varencdistY = encY - encDistY
                        print("varendist Y: ", varencdistY)
                        
                        if encDistY > 0:
                            pin2.write(PT0Y+varencdistY*amp)
                            if 180-PT0Y < UM:
                                PT0Y = 180-UM
                            else:
                                PT0Y = PT0Y + varencdistX*amp
                            print(PT0Y)
                            
                        if encDistY < 0:
                            pin2.write(PT0Y-varencdistX*amp)
                            if PT0Y < DM:
                                PT0Y = DM
                            else:
                                PT0Y = PT0Y - varencdistX*amp
                            print(PT0Y)
                    
                    print("\n")

            #---------------------------------------------------------------
                h, w, c = image.shape
                cx, cy = int(lm.x *w), int(lm.y*h)
                #if id ==0:
                cv2.circle(image, (cx,cy), 3, (255,0,255), cv2.FILLED)

            #mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(image, result.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

#--------------------------------------------------------------------------------------------------
    
        cv2.imshow('Holistic Model Detections', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        cv2.imshow('Camera', cv2.cvtColor(color_frame, cv2.COLOR_BGR2RGB))

        if cv2.waitKey(1) and 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()