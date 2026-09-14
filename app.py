import cv2
import mediapipe as mp
import math


# =========================================
# MediaPipe
# =========================================

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils


# =========================================
# CAMERA
# =========================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open camera")
    exit()


# =========================================
# VIDEO
# =========================================

VIDEO_PATH = "resources/crumbled.mp4"

video = cv2.VideoCapture(VIDEO_PATH)

if not video.isOpened():
    print("Could not open video")
    exit()


# Get total number of video frames

total_frames = int(
    video.get(cv2.CAP_PROP_FRAME_COUNT)
)

print("Total video frames:", total_frames)


# =========================================
# CLOSEDNESS
# =========================================

#qasid's logic 
def get_closedness(hand_landmarks):
    if results.multi_hand_landmarks:

        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):

            # Get Left / Right hand
            hand_label = results.multi_handedness[0].classification[0].label

            # print("Hand:", hand_label,i)
        # Get wrist and middle MCP for angle calculation
    wrist = hand_landmarks.landmark[0]
    middle_mcp = hand_landmarks.landmark[9]

    hand_angle = math.atan2(middle_mcp.y - wrist.y, middle_mcp.x - wrist.x)
    hand_angle_deg = math.degrees(hand_angle)
    norm_angle = hand_angle_deg % 360
    print(norm_angle," Norm Angle")
    if hand_label =='Left':
        print("LEFT HAND DETECTED")
        index_tip = hand_landmarks.landmark[8]
        index_pip = hand_landmarks.landmark[6]

        middle_tip = hand_landmarks.landmark[12]
        middle_pip = hand_landmarks.landmark[10]

        ring_tip = hand_landmarks.landmark[16]
        ring_pip = hand_landmarks.landmark[14]

        pinky_tip = hand_landmarks.landmark[20]
        pinky_pip = hand_landmarks.landmark[18]

        thumb=hand_landmarks.landmark[4]
        fingers_down = 0
        thumb_pinky_check = False
        print(norm_angle, "TRUE TRUE TRUE")
        if (270 <= norm_angle < 360):
       
            #LEFT hand
            #Tumb should be to the right of pinky
            if thumb.x > pinky_tip.x:
               
                thumb_pinky_check = True
                

            if (
                (index_tip.y > index_pip.y) and
                (middle_tip.y > middle_pip.y) and
                (ring_tip.y > ring_pip.y) and
                (pinky_tip.y > pinky_pip.y)
                ):
                print("ALL 4 FINGERS DOWN")
                fingers_down = 4
            return fingers_down / 4.0

        if (norm_angle >= 0) and (norm_angle < 90):
            # print(norm_angle, "TRUE")
            if (thumb.y > pinky_tip.y) or (thumb.y<pinky_tip.y):
                # print("thumb.x =", thumb.x)
                # print("pinky.x =", pinky_tip.x)
                thumb_pinky_check = True

                
            if thumb_pinky_check:
                # print(thumb_pinky_check, "thumb_pinky_check")

                print(
                    "1", index_tip.y > index_pip.y ,
                      "2"  , middle_tip.y > middle_pip.y ,
                        "3" , ring_tip.y > ring_pip.y ,
                            "4",pinky_tip.y > pinky_pip.y 
                 )
                
                if (
                    index_tip.x < index_pip.x and
                    middle_tip.x < middle_pip.x and
                    ring_tip.x < ring_pip.x and
                    pinky_tip.x < pinky_pip.x 
                ):
                 fingers_down = 4
                print(fingers_down, "fingers_down")

            return fingers_down / 4.0
            
        if(180 <= norm_angle  < 270):
            if thumb.y < pinky_tip.y:
                print("thumb.y =", thumb.y)
                print("pinky.y =", pinky_tip.y)
                thumb_pinky_check = True
            if thumb_pinky_check:
                print(thumb_pinky_check, "thumb_pinky_check")
                if (
                    (index_tip.x > index_pip.x) and
                    (middle_tip.x > middle_pip.x) and
                    (ring_tip.x > ring_pip.x) and
                    (pinky_tip.x > pinky_pip.x) 
                                ):
                 
                 
                 


                 fingers_down = 4
                return fingers_down / 4.0
            else:
                return 0
        if(90 <= norm_angle < 180):
            print("thumb.y =", thumb.y)
            print("pinky.y =", pinky_tip.y)
            if thumb.x < pinky_tip.x:
                print("thumb.x =", thumb.x)
                print("pinky.x =", pinky_tip.x)
                if (
                    (index_tip.y < index_pip.y) and
                    (middle_tip.y < middle_pip.y) and
                    (ring_tip.y < ring_pip.y) and
                    (pinky_tip.y < pinky_pip.y)
                    ):
                 
                 fingers_down=4
                 
                return fingers_down/4
            else:
                return 0    
                                 
        else:
            print("out")
            return 0.0 
    elif hand_label == 'Right':

        print("RIGHT HAND DETECTED")
        index_tip = hand_landmarks.landmark[8]
        index_pip = hand_landmarks.landmark[6]

        middle_tip = hand_landmarks.landmark[12]
        middle_pip = hand_landmarks.landmark[10]

        ring_tip = hand_landmarks.landmark[16]
        ring_pip = hand_landmarks.landmark[14]

        pinky_tip = hand_landmarks.landmark[20]
        pinky_pip = hand_landmarks.landmark[18]

        thumb=hand_landmarks.landmark[4]
        fingers_down = 0
        thumb_pinky_check = False
        # For upright (0-90 or 270-360)
        if (norm_angle > 180) and (norm_angle < 270):
            # Right hand upright: thumb should be to the left of pinky
            if thumb.x < pinky_tip.x:
                thumb_pinky_check = True
            # Compare Y: tip should be BELOW pip (y > pip.y)
            if thumb_pinky_check:
                if ((index_tip.y > index_pip.y) and (middle_tip.y > middle_pip.y) and
                    (ring_tip.y > ring_pip.y) and (pinky_tip.y > pinky_pip.y)):
                    fingers_down = 4
            return fingers_down / 4.0


        if (norm_angle >= 90) and (norm_angle < 180):
            print(norm_angle, "TRUE")
            # Right hand upright: thumb should be to the left of pinky
            if thumb.x < pinky_tip.x:
                thumb_pinky_check = True
            # Compare Y: tip should be BELOW pip (y > pip.y)

          
            if thumb_pinky_check:
                if ((index_tip.x > index_pip.x) and (middle_tip.x > middle_pip.x) and
                    (ring_tip.x > ring_pip.x) and (pinky_tip.x > pinky_pip.x)):
                    fingers_down = 4
            return fingers_down / 4.0
        if (norm_angle > 270) and (norm_angle < 360):
            
            # Right hand upright: thumb should be to the left of pinky
            if thumb.x > pinky_tip.x:
                thumb_pinky_check = True
            # Compare Y: tip should be BELOW pip (y > pip.y)
            if thumb_pinky_check:
                if ((index_tip.x < index_pip.x) and (middle_tip.x < middle_pip.x) and
                    (ring_tip.x < ring_pip.x) and (pinky_tip.x < pinky_pip.x)):
                    fingers_down = 4
            return fingers_down / 4.0
        
        if (norm_angle >= 0) and (norm_angle < 90):

            print(norm_angle, "TRUE")

            if thumb.x > pinky_tip.x:

                thumb_pinky_check = True

                if thumb_pinky_check:

                    if ((index_tip.y < index_pip.y) and
                        (middle_tip.y < middle_pip.y) and
                        (ring_tip.y < ring_pip.y) and
                        (pinky_tip.y < pinky_pip.y)):

                        fingers_down = 4

            return fingers_down / 4.0
        
       
        else:
            return 0.0
        # if thumb.x<pinky_tip.x:

        #     if ((index_tip.y > index_pip.y) and (middle_tip.y > middle_pip.y) and
        #     (ring_tip.y > ring_pip.y) and (pinky_tip.y > pinky_pip.y)):
        #         fingers_down=4

        #     return fingers_down / 4.0
        # else:
        #     return fingers_down     
        # return 0




# def get_angle(a, b):
#     dx = a.x - b.x
#     dy = a.y - b.y

#     angle = math.degrees(math.atan2(dy, dx))

#     print(
#         f"[ANGLE] "
#         f"A=({a.x:.3f}, {a.y:.3f}) "
#         f"B=({b.x:.3f}, {b.y:.3f}) "
#         f"dx={dx:.3f} "
#         f"dy={dy:.3f} "
#         f"angle={angle:.2f}°"
#     )

#     return angle

# def get_closedness(hand_landmarks, hand_label):


#     index_tip = hand_landmarks.landmark[8]
#     index_pip = hand_landmarks.landmark[6]

#     middle_tip = hand_landmarks.landmark[12]
#     middle_pip = hand_landmarks.landmark[10]

#     ring_tip = hand_landmarks.landmark[16]
#     ring_pip = hand_landmarks.landmark[14]

#     pinky_tip = hand_landmarks.landmark[20]
#     pinky_pip = hand_landmarks.landmark[18]

#     thumb = hand_landmarks.landmark[4]

#     angle = get_angle(
#         index_pip,
#         index_tip
#     )
#     print("Index angle:", angle)
#     # =====================================
#     # FINGER CLOSED CHECK
#     # =====================================
    

#     # =====================================
#     # CHECK ALL 4 FINGERS CLOSED
#     # =====================================

#     all_Closed=(
#         index_tip.y > index_pip.y and
#         middle_tip.y > middle_pip.y and
#         ring_tip.y > ring_pip.y and
#         pinky_tip.y > pinky_pip.y
#     )

#     if not all_Closed:
#         return 0.0
#     # =====================================
#     # HAND DIRECTION
#     # =====================================
#     if hand_label == "Left":
#         valid_direction = thumb.x > pinky_tip.x
#     else:
#         valid_direction = thumb.x < pinky_tip.x
#     if valid_direction:
#         return 1.0
#     return 0.0


    

# =========================================
# MAIN LOOP
# =========================================

while True:

    # =====================================
    # GET CAMERA FRAME
    # =====================================

    success, frame = cap.read()

    if not success:
        break


    # Mirror webcam

    frame = cv2.flip(frame, 1)


    # =====================================
    # MEDIAPIPE
    # =====================================

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )
    # print(rgb.shape)

    results = hands.process(rgb)


    # Default:
    # video stays at beginning

    closedness = 0.0


    # =====================================
    # DETECT HAND
    # =====================================

    if results.multi_hand_landmarks:

        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):

            # Get Left / Right hand
            hand_label = results.multi_handedness[i].classification[0].label

            print("Hand:", hand_label)


            # Draw hand

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )


            # Get folded finger percentage

            closedness = get_closedness(
                hand_landmarks
            )


    # =====================================
    # CONVERT HAND POSITION
    # TO VIDEO FRAME
    # =====================================

    target_frame = int(
        closedness * (total_frames - 1)
    )


    # Keep frame inside video

    target_frame = max(
        0,
        min(total_frames - 1, target_frame)
    )


    # =====================================
    # JUMP TO VIDEO FRAME
    # =====================================

    video.set(
        cv2.CAP_PROP_POS_FRAMES,
        target_frame
    )


    video_success, video_frame = video.read()


    if not video_success:

        print("Could not read video frame")
        break


    # =====================================
    # SHOW VIDEO
    # =====================================

    cv2.imshow(
        "CRUMBLING VIDEO",
        video_frame
    )


    # =====================================
    # SHOW CAMERA
    # =====================================

    cv2.imshow(
        "HAND CAMERA",
        frame
    )


    # =====================================
    # DEBUG
    # =====================================

    print(
        f"Closedness: {closedness:.2f} | "
        f"Frame: {target_frame}/{total_frames - 1}"
    )


    # =====================================
    # ESC
    # =====================================

    if cv2.waitKey(1) & 0xFF == 27:
        break


# =========================================
# CLEANUP
# =========================================

cap.release()

video.release()

cv2.destroyAllWindows()

hands.close()