import pyautogui
import pygetwindow as gw

previous_y = None


BROWSER_TITLE = "Chrome"


def two_finger_scroll(hand_landmarks, box_y1, box_y2, frame_height):
    global previous_y

    lm = hand_landmarks.landmark

    active_window = gw.getActiveWindow()

    if active_window is None or BROWSER_TITLE.lower() not in active_window.title.lower():
        previous_y = None
        return False

    # =========================================
    # INDEX + MIDDLE UP
    # =========================================

    index_up = lm[8].y < lm[6].y
    middle_up = lm[12].y < lm[10].y

    # =========================================
    # RING + PINKY DOWN
    # =========================================

    ring_down = lm[16].y > lm[14].y
    pinky_down = lm[20].y > lm[18].y

    # =========================================
    # ONLY TWO-FINGER GESTURE
    # =========================================

    if not (
        index_up
        and middle_up
        and ring_down
        and pinky_down
    ):
        previous_y = None
        return False

    # =========================================
    # FINGER POSITION
    # =========================================

    # Use index + middle fingertips
    finger_y = (lm[8].y + lm[12].y) / 2

    # =========================================
    # BOX
    # =========================================

    box_top = box_y1 / frame_height
    box_bottom = box_y2 / frame_height

    # =========================================
    # CHECK FINGERS INSIDE BOX
    # =========================================

    if not (box_top <= finger_y <= box_bottom):
        previous_y = None
        return True

    # =========================================
    # MIDDLE LINE
    # =========================================

    box_middle = (box_top + box_bottom) / 2

    # =========================================
    # AUTOMATIC SCROLL
    # =========================================

    if finger_y < box_middle:

        # Upper half → scroll DOWN
        pyautogui.scroll(-10)

    else:

        # Lower half → scroll UP
        pyautogui.scroll(10)

    return True