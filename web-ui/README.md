# Crumble — Web UI

A standalone React page for the hand-gesture crumble video, completely separate
from `app.py`. It does not need the Python app running — hand tracking happens
directly in the browser using `@mediapipe/tasks-vision`, and it scrubs the
`crumbled.mp4` video based on how closed your hand is.

## Run it

```bash
npm install
npm run dev
```

Then open the printed local URL and click **Start with your camera**
(the browser will ask for camera permission).

## How it works

- `src/useHandTracking.js` loads MediaPipe's `HandLandmarker` model, reads your
  webcam, and computes a 0–1 "closedness" value from the hand landmarks
  (rotation-invariant, based on fingertip-to-wrist vs. knuckle-to-wrist
  distance ratios — no fixed x/y thresholds).
- `src/App.jsx` uses that value to set `video.currentTime` on the crumble
  video and drive the progress bar / status text.
- The video file lives in `public/resources/crumbled.mp4` (a copy of the one
  used by `app.py`).
