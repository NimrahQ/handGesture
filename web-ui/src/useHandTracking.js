import { useCallback, useEffect, useRef, useState } from "react";
import {
  FilesetResolver,
  HandLandmarker,
  DrawingUtils,
} from "@mediapipe/tasks-vision";

// Fingertip / MCP pairs for the four fingers we use to judge how "closed" the hand is.
const FINGERS = [
  [8, 5], // index
  [12, 9], // middle
  [16, 13], // ring
  [20, 17], // pinky
];

// Ratio of (tip distance to wrist) / (mcp distance to wrist) at a fully open
// vs. fully closed hand. Using a ratio of distances (not raw x/y coordinates)
// keeps this working no matter how the hand is rotated in front of the camera.
const OPEN_RATIO = 1.7;
const CLOSED_RATIO = 0.65;
const SMOOTHING = 0.25;

function dist(a, b) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  const dz = (a.z || 0) - (b.z || 0);
  return Math.sqrt(dx * dx + dy * dy + dz * dz);
}

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

function computeClosedness(landmarks) {
  const wrist = landmarks[0];
  let total = 0;

  for (const [tipIdx, mcpIdx] of FINGERS) {
    const tip = landmarks[tipIdx];
    const mcp = landmarks[mcpIdx];
    const ratio = dist(tip, wrist) / (dist(mcp, wrist) || 1e-6);
    const curl = clamp((OPEN_RATIO - ratio) / (OPEN_RATIO - CLOSED_RATIO), 0, 1);
    total += curl;
  }

  return total / FINGERS.length;
}

export function useHandTracking() {
  const videoRef = useRef(null); // raw webcam feed, used only for detection
  const canvasRef = useRef(null); // mirrored frame + landmark skeleton, drawn each tick
  const pipVideoRef = useRef(null); // plays the canvas stream — this is what goes into picture-in-picture
  const landmarkerRef = useRef(null);
  const streamRef = useRef(null);
  const rafRef = useRef(null);
  const smoothedRef = useRef(0);
  const drawingUtilsRef = useRef(null);

  const [closedness, setClosedness] = useState(0);
  const [handLabel, setHandLabel] = useState(null);
  const [handDetected, setHandDetected] = useState(false);
  const [status, setStatus] = useState("idle"); // idle | loading | running | error
  const [error, setError] = useState(null);

  // Load the hand landmark model once on mount.
  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const vision = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm"
        );

        const landmarker = await HandLandmarker.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath:
              "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
            delegate: "GPU",
          },
          runningMode: "VIDEO",
          numHands: 1,
        });

        if (cancelled) {
          landmarker.close();
          return;
        }

        landmarkerRef.current = landmarker;
      } catch (err) {
        console.error("Failed to load hand model:", err);
        if (!cancelled) {
          setError("Could not load the hand-tracking model.");
          setStatus("error");
        }
      }
    })();

    return () => {
      cancelled = true;
      landmarkerRef.current?.close();
      landmarkerRef.current = null;
    };
  }, []);

  const detectLoop = useCallback(() => {
    const video = videoRef.current;
    const landmarker = landmarkerRef.current;
    const canvas = canvasRef.current;

    if (!video || !landmarker || video.readyState < 2) {
      rafRef.current = requestAnimationFrame(detectLoop);
      return;
    }

    const results = landmarker.detectForVideo(video, performance.now());
    const landmarks = results.landmarks?.[0];

    if (landmarks) {
      setHandDetected(true);
      setHandLabel(results.handedness?.[0]?.[0]?.categoryName ?? null);

      const raw = computeClosedness(landmarks);
      smoothedRef.current += (raw - smoothedRef.current) * SMOOTHING;
      setClosedness(smoothedRef.current);
    } else {
      setHandDetected(false);
      setHandLabel(null);
    }

    // Paint the mirrored camera frame plus the hand skeleton onto the
    // canvas that feeds the picture-in-picture window.
    if (canvas) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const ctx = canvas.getContext("2d");
      if (!drawingUtilsRef.current) {
        drawingUtilsRef.current = new DrawingUtils(ctx);
      }

      ctx.save();
      ctx.scale(-1, 1);
      ctx.translate(-canvas.width, 0);
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      if (landmarks) {
        drawingUtilsRef.current.drawConnectors(landmarks, HandLandmarker.HAND_CONNECTIONS, {
          color: "#e0522f",
          lineWidth: 3,
        });
        drawingUtilsRef.current.drawLandmarks(landmarks, {
          color: "#f5efe4",
          lineWidth: 1,
          radius: 3,
        });
      }

      ctx.restore();
    }

    rafRef.current = requestAnimationFrame(detectLoop);
  }, []);

  const start = useCallback(async () => {
    if (status === "running" || status === "loading") return;
    setStatus("loading");
    setError(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
        audio: false,
      });

      streamRef.current = stream;
      const video = videoRef.current;
      video.srcObject = stream;
      await video.play();

      setStatus("running");
      rafRef.current = requestAnimationFrame(detectLoop);

      // Feed the canvas (mirrored frame + skeleton) into the picture-in-
      // picture video. Best-effort and never awaited here — a hiccup in
      // this step must never block the camera from starting.
      if (pipVideoRef.current && canvasRef.current) {
        pipVideoRef.current.srcObject = canvasRef.current.captureStream(30);
        pipVideoRef.current.play().catch((err) => {
          console.error("Picture-in-picture video failed to play:", err);
        });
      }
    } catch (err) {
      console.error("Camera start failed:", err);
      setError(err?.message || "Could not access the camera.");
      setStatus("error");
    }
  }, [status, detectLoop]);

  const stop = useCallback(() => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;

    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;

    if (videoRef.current) videoRef.current.srcObject = null;

    if (pipVideoRef.current?.srcObject) {
      pipVideoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      pipVideoRef.current.srcObject = null;
    }

    smoothedRef.current = 0;
    setClosedness(0);
    setHandDetected(false);
    setHandLabel(null);
    setStatus("idle");
  }, []);

  useEffect(() => {
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  return {
    videoRef,
    canvasRef,
    pipVideoRef,
    closedness,
    handLabel,
    handDetected,
    status,
    error,
    start,
    stop,
  };
}
