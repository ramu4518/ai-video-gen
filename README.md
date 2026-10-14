# AI Video Generator

A local prototype that turns a text prompt into a short Tamil or English video. It combines Groq scene planning, speech synthesis, image assets, and either FFmpeg composition or optional local SadTalker talking-head animation.

## Features

- Generate a structured scene and spoken script from a prompt using Groq.
- Create Tamil or English speech with Edge TTS.
- Select avatar and background assets using `assets/asset_metadata.json`, with fallback assets when a match is unavailable.
- Render a composed video with subtitles and an audio waveform using FFmpeg.
- Optionally animate the selected portrait with SadTalker on a local NVIDIA GPU.
- Use the React/Vite interface for one-step or step-by-step generation and video playback.

## Video Modes

**FFmpeg mode (default):** Composes the scene from a background and image assets. It supports landscape and vertical formats.

**SadTalker mode (optional):** Uses the selected portrait and generated audio to produce a talking-head video. In this project it renders a 256 x 256 face video; it does not animate a full body or include the FFmpeg scene overlays.

The app uses Groq for prompt planning and Edge TTS for speech, so those stages require an internet connection. SadTalker inference itself runs locally after its environment and checkpoints are installed. Provider quotas or charges depend on your account plan.

## Requirements

- Windows 10/11 (the setup below is for Windows)
- Python 3.11 for Flask
- Node.js 22.12+ (Node 22 LTS recommended)
- FFmpeg available on `PATH`
- A Groq API key for scene planning
- Python 3.8 and an NVIDIA CUDA-capable GPU for the optional SadTalker setup

Verify tools from PowerShell:

```powershell
py -3.11 --version
node --version
npm --version
ffmpeg -version
```

## Setup

Run commands from the repository root unless a step says otherwise.

### Backend

Create a Python environment and install the Flask requirements:

```powershell
py -3.11 -m venv backend\venv
backend\venv\Scripts\python.exe -m pip install --upgrade pip
backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Create `backend/.env` and add your own Groq key:

```env
GROQ_API_KEY=your_groq_api_key
```

Do not commit this file or share the key.

### Frontend

```powershell
cd frontend
npm ci
npm run dev
```

Open the URL printed by Vite, usually `http://localhost:5173`.

### Optional SadTalker Setup

SadTalker is a separate environment so its older dependencies do not change the Flask environment. The checkpoint download is about 3 GB and is not included in the repository.

Install Python 3.8 if needed, then create the environment and install dependencies:

```powershell
py -3.8 -m venv backend\.venv-sadtalker
backend\.venv-sadtalker\Scripts\python.exe -m pip install --upgrade pip
backend\.venv-sadtalker\Scripts\python.exe -m pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113
backend\.venv-sadtalker\Scripts\python.exe -m pip install lmdb==1.4.1
backend\.venv-sadtalker\Scripts\python.exe -m pip install -r backend\models\SadTalker\requirements.txt
backend\.venv-sadtalker\Scripts\python.exe -m pip install hf_xet
```

Download the legacy checkpoints from the upstream Hugging Face repository into `backend/models/SadTalker/checkpoints`:

```powershell
backend\.venv-sadtalker\Scripts\python.exe -c "from huggingface_hub import hf_hub_download; files = ['auido2exp_00300-model.pth', 'auido2pose_00140-model.pth', 'epoch_20.pth', 'facevid2vid_00189-model.pth.tar', 'mapping_00229-model.pth.tar', 'wav2lip.pth']; [hf_hub_download(repo_id='vinthony/SadTalker', filename=name, local_dir='backend/models/SadTalker/checkpoints') for name in files]"
```

SadTalker checkpoints and third-party assets have their own licenses. Review those terms before redistribution. MediaPipe is not required by this inference path.

## Run the App

Start the backend in one PowerShell terminal from the repository root. To use the default FFmpeg renderer, run:

```powershell
backend\venv\Scripts\python.exe backend\app.py
```

To enable SadTalker instead, set its environment variables in that same terminal before starting Flask:

```powershell
$env:SADTALKER_ENABLED = "true"
$env:SADTALKER_PYTHON = (Resolve-Path "backend\.venv-sadtalker\Scripts\python.exe").Path
backend\venv\Scripts\python.exe backend\app.py
```

Keep the frontend running in a second terminal with `npm run dev`. Enter a prompt in the browser and generate a video. The backend writes generated media to `output/`; the final video is `output/final_video.mp4`.

## API

The local Flask API listens on `http://127.0.0.1:5000`.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/` | Backend status and capabilities |
| `POST` | `/plan-scene` | Create a scene plan from a prompt |
| `POST` | `/generate-audio` | Generate speech from a script |
| `POST` | `/generate-video` | Render a supplied scene, using existing/generated audio |
| `POST` | `/generate-full-video` | Plan, synthesize speech, and render in one request |
| `GET` | `/video/<filename>` | Serve generated audio or video |

Example full-video request:

```json
{
  "prompt": "A farmer explains how to conserve rainwater.",
  "language": "English",
  "gender": "Male",
  "aspect_ratio": "16:9"
}
```

## Project Layout

```text
assets/                     Avatar, background, and prop images plus metadata
backend/app.py              Flask API and generation workflow
backend/scene_composer.py   FFmpeg scene composition
backend/sadtalker_runner.py Optional local SadTalker subprocess integration
backend/models/SadTalker/   SadTalker source code
frontend/                   React and Vite application
output/                     Generated media (ignored by Git)
```

## Current Limitations

- The app creates a single short scene, not a multi-scene timeline.
- SadTalker produces face/head motion, not full-body animation.
- SadTalker generation can take several minutes and requires substantial RAM, GPU memory, and disk space.
- Generated output filenames are reused, so a new generation replaces the previous final video and audio.
- Scene planning and speech synthesis require their online services; only the SadTalker inference step is local.

## GitHub Upload Notes

The root `.gitignore` excludes virtual environments, generated media, and SadTalker checkpoints. Do not force-add those large files or `backend/.env`. Check before pushing:

```powershell
git status --short
```

Only publish images, fonts, model files, and other assets when their licenses permit redistribution. This repository does not currently declare a top-level project license; add one before granting reuse rights to the project as a whole.

## Verification

The Windows setup has been tested with the Flask endpoint, the FFmpeg renderer, and SadTalker inference on an NVIDIA RTX 2050. A 26-second SadTalker video completed successfully. This is a development prototype, not a production deployment."# ai-video-gen" 
