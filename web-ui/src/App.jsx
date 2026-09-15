import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useHandTracking } from "./useHandTracking";
import "./App.css";

function statusLabel(value, handDetected) {
  if (!handDetected) return "SHOW YOUR HAND";
  if (value < 0.12) return "OPEN HAND";
  if (value < 0.35) return "BEGIN FOLDING";
  if (value < 0.7) return "FOLDING";
  if (value < 0.9) return "ALMOST CLOSED";
  return "FULL FIST";
}

const RESPONSE_STAGES = [
  { range: "0 – 12%", label: "Open hand", note: "Paper stays flat." },
  { range: "12 – 35%", label: "Begin folding", note: "First creases appear." },
  { range: "35 – 70%", label: "Folding", note: "Folds deepen across the face." },
  { range: "70 – 90%", label: "Almost closed", note: "Only a few flat patches remain." },
  { range: "90 – 100%", label: "Full fist", note: "Nothing flat is left." },
];

const BUILD_POINTS = [
  {
    title: "Runs in your browser",
    body: "Hand tracking uses MediaPipe's HandLandmarker (@mediapipe/tasks-vision), loaded and run entirely client-side — no server, no video upload.",
  },
  {
    title: "Rotation-independent reading",
    body: "Closedness is computed from fingertip-to-wrist vs. knuckle-to-wrist distance ratios, so it holds up no matter how your hand is angled.",
  },
  {
    title: "Camera stays out of the page",
    body: "The feed is read for tracking only. If you want to see your gesture, it opens in the browser's own picture-in-picture window instead of sitting in the layout.",
  },
];

export default function App() {
  const {
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
  } = useHandTracking();

  const videoElRef = useRef(null);
  const percent = Math.round(closedness * 100);
  const running = status === "running";

  const [pipActive, setPipActive] = useState(false);
  const pipSupported =
    typeof document !== "undefined" && document.pictureInPictureEnabled;

  const label = useMemo(
    () => statusLabel(closedness, handDetected),
    [closedness, handDetected]
  );

  // Let the skeleton-overlaid camera feed float in the browser/OS's own
  // picture-in-picture window — a real floating window, not part of this
  // page's layout — so you can still see the gesture you're making.
  const showCameraWindow = useCallback(async () => {
    try {
      const pipVideo = pipVideoRef.current;
      if (!pipVideo) return;

      if (pipVideo.paused) {
        await pipVideo.play();
      }

      if (document.pictureInPictureElement !== pipVideo) {
        await pipVideo.requestPictureInPicture();
      }
    } catch (err) {
      console.error("Picture-in-picture failed:", err);
    }
  }, [pipVideoRef]);

  useEffect(() => {
    const pipVideo = pipVideoRef.current;
    if (!pipVideo) return;

    const onEnter = () => setPipActive(true);
    const onLeave = () => setPipActive(false);

    pipVideo.addEventListener("enterpictureinpicture", onEnter);
    pipVideo.addEventListener("leavepictureinpicture", onLeave);

    return () => {
      pipVideo.removeEventListener("enterpictureinpicture", onEnter);
      pipVideo.removeEventListener("leavepictureinpicture", onLeave);
    };
  }, [pipVideoRef]);

  // Drop the picture-in-picture window when the camera stops.
  useEffect(() => {
    if (!running && document.pictureInPictureElement) {
      document.exitPictureInPicture().catch(() => {});
    }
  }, [running]);

  // Drive the crumble video's playhead from the live closedness value.
  useEffect(() => {
    const el = videoElRef.current;
    if (!el || !el.duration || !isFinite(el.duration)) return;

    const target = closedness * el.duration;
    if (Math.abs(el.currentTime - target) > 0.01) {
      el.currentTime = target;
    }
  }, [closedness]);

  return (
    <div className="page" id="top">
      <nav>
        <div className="logo">CRUMBLE</div>
        <div className="nav-links">
          <a href="#material">Material</a>
          <a href="#response">Response</a>
          <a href="#build">Build</a>
        </div>
      </nav>

      <main>
        <section className="left">
          <div className="red-line" />
          <div className="eyebrow">A gesture-driven experiment</div>

          <h1>
            Paper
            <br />
            remembers
            <br />
            every fold.
          </h1>

          <p className="description">
            A printed face, cut and creased by hand, watches your webcam.
            Close your fist and the paper closes with it — fold by fold,
            until nothing flat is left.
          </p>

          {status !== "running" && (
            <button
              className="start-button"
              onClick={start}
              disabled={status === "loading"}
            >
              {status === "loading" ? "Starting camera…" : "Start with your camera"}
              <span className="arrow">→</span>
            </button>
          )}

          {status === "running" && (
            <div className="button-row">
              <button className="start-button stop" onClick={stop}>
                Stop camera
              </button>

              {pipSupported && (
                <button
                  className="start-button ghost"
                  onClick={pipActive ? () => document.exitPictureInPicture() : showCameraWindow}
                >
                  {pipActive ? "Hide camera window" : "See your hand"}
                </button>
              )}
            </div>
          )}

          {error && <p className="error-text">{error}</p>}

          <div className={`interaction ${running ? "active" : ""}`}>
            <div className="interaction-header">
              <span>
                {label}
                {handLabel && running ? ` · ${handLabel.toUpperCase()} HAND` : ""}
              </span>
              <span>{percent}%</span>
            </div>
            <div className="progress-track">
              <div className="progress" style={{ width: `${percent}%` }} />
            </div>
          </div>
        </section>

        <section className="right">
          <div className="video-wrapper">
            <video
              ref={videoElRef}
              muted
              playsInline
              preload="auto"
              loop={false}
            >
              <source src="/resources/crumbled.mp4" type="video/mp4" />
            </video>

            <div className="video-label">MATERIAL / 01</div>

            <div className="camera-status">
              <span className={`dot ${running ? "live" : ""}`} />
              {running ? "CAMERA LIVE" : status === "error" ? "CAMERA ERROR" : "CAMERA OFF"}
            </div>
          </div>

          {/* Nothing here renders inline in the UI. The raw webcam feed
              (videoRef) is read for tracking only; the canvas draws the
              mirrored frame plus the hand-connection skeleton; pipVideoRef
              plays that canvas and is the element popped into the OS
              picture-in-picture window above. */}
          <video ref={videoRef} className="offscreen" muted playsInline />
          <canvas ref={canvasRef} className="offscreen" />
          <video ref={pipVideoRef} className="offscreen" muted playsInline />
        </section>
      </main>

      <section id="material" className="content-section">
        <div className="section-heading">
          <div className="red-line" />
          <div className="eyebrow">01 / Material</div>
          <h2>A face built to fold</h2>
        </div>

        <div className="material-grid">
          <div className="material-card">
            <span className="material-index">Cut</span>
            <p>
              The portrait is scored along its features first, so every crease
              has somewhere planned to go.
            </p>
          </div>
          <div className="material-card">
            <span className="material-index">Creased</span>
            <p>
              Each fold is pre-worked into the paper by hand, frame by frame,
              long before your hand ever closes.
            </p>
          </div>
          <div className="material-card">
            <span className="material-index">Watched</span>
            <p>
              Your webcam only ever supplies one number — how closed your
              hand is — and that number scrubs straight through the reel.
            </p>
          </div>
        </div>
      </section>

      <section id="response" className="content-section">
        <div className="section-heading">
          <div className="red-line" />
          <div className="eyebrow">02 / Response</div>
          <h2>Five stages, one gesture</h2>
        </div>

        <div className="stages">
          {RESPONSE_STAGES.map((stage) => (
            <div className="stage-card" key={stage.label}>
              <span className="stage-range">{stage.range}</span>
              <span className="stage-label">{stage.label}</span>
              <p className="stage-note">{stage.note}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="build" className="content-section">
        <div className="section-heading">
          <div className="red-line" />
          <div className="eyebrow">03 / Build</div>
          <h2>How it's put together</h2>
        </div>

        <div className="build-grid">
          {BUILD_POINTS.map((point) => (
            <div className="build-card" key={point.title}>
              <h3>{point.title}</h3>
              <p>{point.body}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="page-footer">
        <span>CRUMBLE — a gesture-driven experiment</span>
        <a href="#top" className="back-to-top">
          Back to top ↑
        </a>
      </footer>
    </div>
  );
}
