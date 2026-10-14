import { useState } from "react";
import "./App.css";

const PRESET_PROMPTS = [
  {
    title: "🌾 Farmer • Water Conservation",
    prompt: "Create a 20-second video of a Tamil farmer explaining rainwater harvesting and water conservation in a village.",
    lang: "Tamil",
    gender: "Male"
  },
  {
    title: "🩺 Doctor • Health Habits",
    prompt: "A friendly doctor explaining 3 essential daily habits for a healthy heart and active lifestyle.",
    lang: "Tamil",
    gender: "Female"
  },
  {
    title: "📚 Student • Exam Success",
    prompt: "A motivated student sharing high-impact study techniques and memory tips for scoring high in exams.",
    lang: "English",
    gender: "Male"
  },
  {
    title: "💼 Leader • Growth Mindset",
    prompt: "A successful entrepreneur sharing the mindset shift required to turn failures into breakthrough success.",
    lang: "English",
    gender: "Male"
  },
  {
    title: "👩‍🏫 Teacher • Reading Habit",
    prompt: "An inspiring school teacher explaining why reading books daily transforms young minds.",
    lang: "Tamil",
    gender: "Female"
  }
];

function App() {
  const [prompt, setPrompt] = useState(PRESET_PROMPTS[0].prompt);
  const [language, setLanguage] = useState("Tamil");
  const [gender, setGender] = useState("Male");
  const [aspectRatio, setAspectRatio] = useState("16:9");

  const [stepByStep, setStepByStep] = useState(false);
  const [currentStep, setCurrentStep] = useState(0); // 0: idle, 1: planning, 2: audio, 3: rendering, 4: done
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [scene, setScene] = useState(null);
  const [audioReady, setAudioReady] = useState(false);
  const [videoReady, setVideoReady] = useState(false);
  const [videoFile, setVideoFile] = useState("final_video.mp4");
  const [copied, setCopied] = useState(false);

  // Apply Preset Chip
  const applyPreset = (preset) => {
    setPrompt(preset.prompt);
    setLanguage(preset.lang);
    setGender(preset.gender);
    setError("");
  };

  // ----------------------------------------------------
  // 1-CLICK COMPLETE REAL-TIME PIPELINE
  // ----------------------------------------------------
  const generateFullVideo = async () => {
    if (!prompt.trim()) {
      setError("Please enter a video prompt.");
      return;
    }

    setLoading(true);
    setError("");
    setCurrentStep(1);
    setVideoReady(false);
    setAudioReady(false);

    try {
      // Step 1 & 2 & 3 in single backend call
      const res = await fetch("http://127.0.0.1:5000/generate-full-video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          language,
          gender,
          aspect_ratio: aspectRatio
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to generate video");

      setScene(data.scene);
      setAudioReady(true);
      setVideoFile(data.video || "final_video.mp4");
      setVideoReady(true);
      setCurrentStep(4);
    } catch (err) {
      setError(err.message);
      setCurrentStep(0);
    } finally {
      setLoading(false);
    }
  };

  // ----------------------------------------------------
  // STEP-BY-STEP: 1. PLAN SCENE
  // ----------------------------------------------------
  const handlePlanScene = async () => {
    if (!prompt.trim()) {
      setError("Please enter a prompt.");
      return;
    }
    setLoading(true);
    setError("");
    setCurrentStep(1);

    try {
      const res = await fetch("http://127.0.0.1:5000/plan-scene", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          language,
          gender,
          aspect_ratio: aspectRatio
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Scene planning failed");

      setScene(data.scene);
      setAudioReady(false);
      setVideoReady(false);
      setCurrentStep(2);
    } catch (err) {
      setError(err.message);
      setCurrentStep(0);
    } finally {
      setLoading(false);
    }
  };

  // ----------------------------------------------------
  // STEP-BY-STEP: 2. GENERATE AUDIO
  // ----------------------------------------------------
  const handleGenerateAudio = async () => {
    if (!scene) return;
    setLoading(true);
    setError("");
    setCurrentStep(2);

    try {
      const res = await fetch("http://127.0.0.1:5000/generate-audio", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          script: scene.script,
          voice: scene.voice
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Voice synthesis failed");

      setAudioReady(true);
      setCurrentStep(3);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ----------------------------------------------------
  // STEP-BY-STEP: 3. GENERATE VIDEO
  // ----------------------------------------------------
  const handleGenerateVideo = async () => {
    if (!scene) return;
    setLoading(true);
    setError("");
    setCurrentStep(3);

    try {
      const res = await fetch("http://127.0.0.1:5000/generate-video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scene })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Video rendering failed");

      setVideoFile(data.video || "final_video.mp4");
      setVideoReady(true);
      setCurrentStep(4);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Copy Script to Clipboard
  const copyScript = () => {
    if (scene && scene.script) {
      navigator.clipboard.writeText(scene.script);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="studio-container">
      {/* Studio Header */}
      <header className="studio-header">
        <div>
          <div className="brand-badge">⚡ AI VIDEO STUDIO PRO 2.0</div>
          <h1 className="studio-title">Autonomous AI Video Generator</h1>
          <p className="studio-subtitle">
            Multilingual Text-to-Video Engine • Groq AI • Neural Voice Synthesis • FFmpeg Studio Compositor
          </p>
        </div>
        <div className="engine-status">
          <span className="pulse-dot"></span>
          Engine Online & Ready
        </div>
      </header>

      {/* Main Studio Card */}
      <div className="glass-card">
        {/* Preset Chips */}
        <label className="control-label" style={{ display: "block", marginBottom: "8px" }}>
          💡 Quick Inspiration Prompts:
        </label>
        <div className="chips-container">
          {PRESET_PROMPTS.map((p, idx) => (
            <button
              key={idx}
              className="chip"
              onClick={() => applyPreset(p)}
              type="button"
            >
              {p.title}
            </button>
          ))}
        </div>

        {/* Prompt Input */}
        <textarea
          className="prompt-box"
          rows="4"
          placeholder="Describe your video idea in detail (e.g. A doctor explaining the benefits of hydration in Tamil, or a student sharing study tips in English)..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />

        {/* Configuration Bar */}
        <div className="controls-bar">
          {/* Language Toggle */}
          <div className="control-group">
            <span className="control-label">🌐 Spoken Language:</span>
            <div className="toggle-pill">
              <button
                type="button"
                className={`toggle-option ${language === "Tamil" ? "active" : ""}`}
                onClick={() => setLanguage("Tamil")}
              >
                Tamil (தமிழ்)
              </button>
              <button
                type="button"
                className={`toggle-option ${language === "English" ? "active" : ""}`}
                onClick={() => setLanguage("English")}
              >
                English
              </button>
            </div>
          </div>

          {/* Voice Gender Toggle */}
          <div className="control-group">
            <span className="control-label">🎙️ Voice Gender:</span>
            <div className="toggle-pill">
              <button
                type="button"
                className={`toggle-option ${gender === "Male" ? "active" : ""}`}
                onClick={() => setGender("Male")}
              >
                Male
              </button>
              <button
                type="button"
                className={`toggle-option ${gender === "Female" ? "active" : ""}`}
                onClick={() => setGender("Female")}
              >
                Female
              </button>
            </div>
          </div>

          {/* Aspect Ratio Toggle */}
          <div className="control-group">
            <span className="control-label">📐 Aspect Ratio:</span>
            <div className="toggle-pill">
              <button
                type="button"
                className={`toggle-option ${aspectRatio === "16:9" ? "active" : ""}`}
                onClick={() => setAspectRatio("16:9")}
              >
                16:9 (Landscape)
              </button>
              <button
                type="button"
                className={`toggle-option ${aspectRatio === "9:16" ? "active" : ""}`}
                onClick={() => setAspectRatio("9:16")}
              >
                9:16 (Shorts/Reels)
              </button>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="actions-row">
          <button
            className="btn-primary"
            onClick={generateFullVideo}
            disabled={loading}
          >
            {loading && currentStep > 0
              ? `⚡ Generating Studio Video...`
              : `✨ Generate Full Video (1-Click)`}
          </button>

          <button
            type="button"
            className="btn-secondary"
            onClick={() => setStepByStep(!stepByStep)}
          >
            {stepByStep ? "Hide Manual Controls" : "🛠️ Step-by-Step Mode"}
          </button>
        </div>

        {/* Step-by-Step Sub-controls (Optional Mode) */}
        {stepByStep && (
          <div style={{ marginTop: "18px", paddingTop: "16px", borderTop: "1px dashed var(--border-color)", display: "flex", gap: "10px", flexWrap: "wrap" }}>
            <button
              className="btn-secondary"
              onClick={handlePlanScene}
              disabled={loading}
            >
              1. Plan Scene & Script
            </button>
            <button
              className="btn-secondary"
              onClick={handleGenerateAudio}
              disabled={loading || !scene}
            >
              2. Generate Voice Audio
            </button>
            <button
              className="btn-secondary"
              onClick={handleGenerateVideo}
              disabled={loading || !scene}
            >
              3. Render Final Video
            </button>
          </div>
        )}

        {/* Error Notification */}
        {error && (
          <div className="error-banner">
            ⚠️ <strong>Error:</strong> {error}
          </div>
        )}
      </div>

      {/* Live Pipeline Stepper */}
      {loading && (
        <div className="stepper-card">
          <div className="stepper-list">
            <div className={`step-item ${currentStep === 1 ? "active" : currentStep > 1 ? "done" : ""}`}>
              <span className="step-icon">🧠</span>
              <div>
                <p className="step-title">1. Scene Planning</p>
                <p className="step-desc">Generating structured script via Groq AI...</p>
              </div>
            </div>

            <div className={`step-item ${currentStep === 2 ? "active" : currentStep > 2 ? "done" : ""}`}>
              <span className="step-icon">🎙️</span>
              <div>
                <p className="step-title">2. Voice Synthesis</p>
                <p className="step-desc">Synthesizing audio ({language} {gender})...</p>
              </div>
            </div>

            <div className={`step-item ${currentStep === 3 ? "active" : currentStep > 3 ? "done" : ""}`}>
              <span className="step-icon">🎨</span>
              <div>
                <p className="step-title">3. Visual Sourcing</p>
                <p className="step-desc">Framing character & backdrop...</p>
              </div>
            </div>

            <div className={`step-item ${currentStep === 4 ? "active" : ""}`}>
              <span className="step-icon">🎬</span>
              <div>
                <p className="step-title">4. Studio Render</p>
                <p className="step-desc">FFmpeg compositing subtitles & waveform...</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Output Studio Section */}
      {(scene || videoReady) && (
        <div className="studio-output-grid">
          {/* Left Column: Script & Scene Details */}
          <div className="glass-card">
            <h2 className="section-heading">
              <span>📋 Scene & Script Details</span>
              {scene && (
                <button
                  type="button"
                  onClick={copyScript}
                  className="btn-secondary"
                  style={{ padding: "4px 10px", fontSize: "12px" }}
                >
                  {copied ? "✓ Copied" : "📋 Copy"}
                </button>
              )}
            </h2>

            {scene && (
              <>
                <div className="meta-tags-row">
                  <span className="meta-tag">👤 {scene.character}</span>
                  <span className="meta-tag">🏞️ {scene.background}</span>
                  <span className="meta-tag">🎥 {scene.camera}</span>
                  <span className="meta-tag">⏱️ {scene.duration || 20}s</span>
                  <span className="meta-tag">🗣️ {scene.voice?.language} ({scene.voice?.gender})</span>
                </div>

                <div className="script-box">
                  "{scene.script}"
                </div>

                {/* Visual Asset Previews */}
                <label className="control-label">🖼️ Selected Visual Assets:</label>
                <div className="assets-preview-row">
                  <div className="asset-thumb-card">
                    <img
                      src={`http://127.0.0.1:5000/asset-preview/avatars/${scene.character}`}
                      alt={scene.character}
                      onError={(e) => { e.target.src = "http://127.0.0.1:5000/asset-preview/avatars/Farmer"; }}
                    />
                    <span>Presenter: {scene.character}</span>
                  </div>

                  <div className="asset-thumb-card">
                    <img
                      src={`http://127.0.0.1:5000/asset-preview/backgrounds/${scene.background}`}
                      alt={scene.background}
                      onError={(e) => { e.target.src = "http://127.0.0.1:5000/asset-preview/backgrounds/Village"; }}
                    />
                    <span>Scenery: {scene.background}</span>
                  </div>
                </div>

                {/* Voice Preview */}
                {audioReady && (
                  <div style={{ marginTop: "20px" }}>
                    <label className="control-label" style={{ display: "block", marginBottom: "6px" }}>
                      🔊 Synthesized Speech Audio:
                    </label>
                    <audio
                      key={Date.now()}
                      controls
                      style={{ width: "100%", height: "40px" }}
                    >
                      <source
                        src={`http://127.0.0.1:5000/video/scene_audio.mp3?t=${Date.now()}`}
                        type="audio/mpeg"
                      />
                    </audio>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Right Column: Final Video Display */}
          <div className="glass-card" style={{ display: "flex", flexDirection: "column" }}>
            <h2 className="section-heading">
              <span>🎬 Rendered Video Player</span>
              {videoReady && (
                <a
                  href={`http://127.0.0.1:5000/video/${videoFile}`}
                  download="ai_generated_video.mp4"
                  className="btn-secondary"
                  style={{ textDecoration: "none", padding: "6px 14px", fontSize: "13px" }}
                >
                  ⬇️ Download MP4
                </a>
              )}
            </h2>

            <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
              {videoReady ? (
                <div className={`video-wrapper ${aspectRatio === "9:16" ? "portrait" : "landscape"}`}>
                  <video
                    key={videoFile + Date.now()}
                    controls
                    autoPlay
                    playsInline
                  >
                    <source
                      src={`http://127.0.0.1:5000/video/${videoFile}?t=${Date.now()}`}
                      type="video/mp4"
                    />
                    Your browser does not support the video tag.
                  </video>
                </div>
              ) : (
                <div style={{ textAlign: "center", padding: "40px 20px", color: "var(--text-muted)" }}>
                  <div style={{ fontSize: "44px", marginBottom: "12px" }}>📺</div>
                  <p style={{ margin: 0, fontSize: "15px" }}>
                    {loading ? "Compositing video with animated subtitles & waveform..." : "Your rendered studio video will appear here."}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
