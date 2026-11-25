import pyautogui
import pygetwindow as gw

previous_y = None

# No built-in 100 ms delay after every pyautogui call (it made scrolling choppy)
pyautogui.PAUSE = 0

# Smoothing state / tuning
smooth_y = None
velocity = 0.0
scroll_accum = 0.0

POSITION_SMOOTHING = 0.35   # 0..1, lower = smoother fingertip tracking
VELOCITY_SMOOTHING = 0.15   # 0..1, lower = gentler speed up / slow down
DEAD_ZONE = 0.15            # fraction of box half-height around the middle
MAX_SPEED = 40              # wheel units per frame at the box edge


def _reset_smoothing():
    global smooth_y, velocity, scroll_accum
    smooth_y = None
    velocity = 0.0
    scroll_accum = 0.0


# Only scroll when the active tab is this site. The browser window title is
# "<page title> - Google Chrome", so matching "Chrome" also matched YouTube,
# LinkedIn, etc. Match the page's own <title> instead.
BROWSER_TITLE = "CRUMBLE"


def _find_site_window():
    """Return the browser window showing this site, or None."""
    try:
        for w in gw.getAllWindows():
            if BROWSER_TITLE.lower() in w.title.lower() and not w.isMinimized:
                return w
    except Exception:
        pass
    return None


def _focus_site_window():
    """Bring the site's window to the front and park the cursor over it, so
    wheel events reach the page without a manual click first."""
    win = _find_site_window()
    if win is None:
        return None
    try:
        if gw.getActiveWindow() is None or win._hWnd != gw.getActiveWindow()._hWnd:
            # Windows may refuse SetForegroundWindow from a background
            # process; a tapped Alt key lifts that restriction.
            pyautogui.press("alt")
            win.activate()
        x, y = pyautogui.position()
        if not (win.left <= x <= win.left + win.width and win.top <= y <= win.top + win.height):
            pyautogui.moveTo(win.left + win.width // 2, win.top + win.height // 2)
    except Exception:
        pass
    return win


def two_finger_scroll(hand_landmarks, box_y1, box_y2, frame_height):
    global previous_y, smooth_y, velocity, scroll_accum

    lm = hand_landmarks.landmark

    # Only act if the site's window exists at all (otherwise don't scroll
    # whatever else is on screen).
    if _find_site_window() is None:
        previous_y = None
        _reset_smoothing()
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
        _reset_smoothing()
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
        _reset_smoothing()
        return True

    # =========================================
    # MIDDLE LINE
    # =========================================

    box_middle = (box_top + box_bottom) / 2

    # Gesture confirmed: make sure the page has focus and the cursor is over it
    _focus_site_window()

    # =========================================
    # AUTOMATIC SCROLL
    # =========================================

    # Smooth the raw fingertip position to remove camera jitter
    if smooth_y is None:
        smooth_y = finger_y
    else:
        smooth_y += (finger_y - smooth_y) * POSITION_SMOOTHING

    # Offset from the middle line: -1 (top edge) .. +1 (bottom edge)
    half = (box_bottom - box_top) / 2
    offset = max(-1.0, min(1.0, (smooth_y - box_middle) / half))

    # Dead zone around the middle line, then speed grows with distance
    if abs(offset) < DEAD_ZONE:
        target = 0.0
    else:
        sign = 1 if offset > 0 else -1
        target = sign * (abs(offset) - DEAD_ZONE) / (1 - DEAD_ZONE) * MAX_SPEED

    # Ease current speed toward the target (acceleration / deceleration)
    velocity += (target - velocity) * VELOCITY_SMOOTHING

    # Lower half → scroll UP (positive), upper half → scroll DOWN (negative).
    # Accumulate fractions so slow speeds still scroll evenly.
    scroll_accum += velocity
    steps = int(scroll_accum)
    if steps:
        scroll_accum -= steps
        pyautogui.scroll(steps)

    return True