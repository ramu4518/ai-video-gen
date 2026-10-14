from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from tts import create_audio
from scene_composer import create_scene, resolve_asset_path
from sadtalker_runner import is_enabled as sadtalker_enabled, render_talking_head
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
os.makedirs(OUTPUT_DIR, exist_ok=True)

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(ENV_PATH)

# --------------------------------------------------
# FLASK APP
# --------------------------------------------------

app = Flask(__name__)
CORS(app)

# --------------------------------------------------
# GROQ CLIENT
# --------------------------------------------------

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


# --------------------------------------------------
# HOME & HEALTH CHECK
# --------------------------------------------------

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "service": "AI Video Generator Studio API",
        "version": "2.0.0",
        "capabilities": [
            "Tamil & English Multi-lingual Script Planning",
            "Neural Voice Synthesis (Edge-TTS & gTTS)",
            "Ken Burns Motion & Subtitle Rendering",
            "Audio Waveform Visualization",
            "16:9 Landscape & 9:16 Vertical Video Formats"
        ]
    })


# --------------------------------------------------
# SCENE PLANNER
# --------------------------------------------------

@app.route("/plan-scene", methods=["POST"])
def plan_scene():
    data = request.get_json() or {}
    user_prompt = data.get("prompt")
    pref_lang = data.get("language")
    pref_gender = data.get("gender")
    aspect_ratio = data.get("aspect_ratio", "16:9")

    if not user_prompt:
        return jsonify({
            "success": False,
            "error": "Prompt is required"
        }), 400

    system_prompt = f"""
You are an expert AI Video Scene & Script Director.

Convert the user's video concept into a tight, highly engaging 15-30 second video script with full scene metadata.
Return ONLY valid JSON.

Use exactly this structure:
{{
  "duration": number,
  "language": "Tamil" or "English",
  "character": "",
  "background": "",
  "script": "",
  "action": "",
  "expression": "",
  "props": [],
  "camera": "",
  "voice": {{
    "gender": "Male" or "Female",
    "language": "Tamil" or "English"
  }},
  "aspect_ratio": "{aspect_ratio}"
}}

Available characters:
Farmer, Student, Doctor, Businessman, Teacher, Scientist

Available backgrounds:
Village, Farm, Hospital, School, Office, City, College, Lab

Available motions/actions:
Talk, Explain, Wave, Point, Think, Demonstrate

Available expressions:
Neutral, Happy, Inspiring, Serious, Excited, Friendly

Available camera movements:
Zoom In, Zoom Out, Static, Close-up

Rules:
- Generate a natural, impactful spoken dialogue/script (2 to 4 sentences).
- If preferred language is provided as '{pref_lang}', you MUST use that language. Otherwise detect from prompt or default to Tamil for rural/Tamil prompts, English for global/tech.
- If language is Tamil, write the script strictly in Tamil script (Unicode).
- If preferred gender is provided as '{pref_gender}', use that gender.
- Return ONLY the raw JSON object. Do not add markdown fences, commentary, or text.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        result = response.choices[0].message.content.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[-1]
            if result.endswith("```"):
                result = result.rsplit("```", 1)[0]

        scene = json.loads(result.strip())
        scene["aspect_ratio"] = aspect_ratio

        return jsonify({
            "success": True,
            "scene": scene
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Scene planning error: {str(e)}"
        }), 500


# --------------------------------------------------
# TEXT TO SPEECH
# --------------------------------------------------

@app.route("/generate-audio", methods=["POST"])
def generate_audio():
    data = request.json or {}
    script = data.get("script")
    voice = data.get("voice", {})

    language = voice.get("language", "Tamil")
    gender = voice.get("gender", "Male")

    if not script:
        return jsonify({
            "success": False,
            "error": "Script is required"
        }), 400

    output_file = os.path.join(OUTPUT_DIR, "scene_audio.mp3")

    try:
        create_audio(
            script,
            output_file,
            language,
            gender
        )

        return jsonify({
            "success": True,
            "audio": "scene_audio.mp3"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Voice synthesis error: {str(e)}"
        }), 500


def render_video(scene, audio_file, output_file):
    if sadtalker_enabled():
        return render_talking_head(scene, audio_file, output_file)
    return create_scene(scene, audio_file=audio_file, output_file=output_file)


# --------------------------------------------------
# GENERATE FINAL VIDEO
# --------------------------------------------------

@app.route("/generate-video", methods=["POST"])
def generate_video():
    data = request.json or {}
    scene = data.get("scene")

    if not scene:
        return jsonify({
            "success": False,
            "error": "Scene data is required"
        }), 400

    try:
        # 1. Ensure audio exists or generate it
        audio_file = os.path.join(OUTPUT_DIR, "scene_audio.mp3")
        script = scene.get("script", "")
        voice = scene.get("voice", {})
        language = voice.get("language", "Tamil")
        gender = voice.get("gender", "Male")

        if not os.path.exists(audio_file) or os.path.getsize(audio_file) < 500:
            create_audio(script, audio_file, language, gender)

        # 2. Render Video with Subtitles and Waveform
        final_video_path = os.path.join(OUTPUT_DIR, "final_video.mp4")
        render_video(scene, audio_file, final_video_path)

        return jsonify({
            "success": True,
            "video": "final_video.mp4"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Video rendering error: {str(e)}"
        }), 500


# --------------------------------------------------
# 1-CLICK COMPLETE REAL-TIME PIPELINE
# --------------------------------------------------

@app.route("/generate-full-video", methods=["POST"])
def generate_full_video():
    data = request.json or {}
    user_prompt = data.get("prompt")
    pref_lang = data.get("language")
    pref_gender = data.get("gender")
    aspect_ratio = data.get("aspect_ratio", "16:9")

    if not user_prompt:
        return jsonify({
            "success": False,
            "error": "Prompt is required"
        }), 400

    try:
        # Step 1: Plan Scene
        system_prompt = f"""
You are an expert AI Video Scene & Script Director.
Convert the user's idea into a compelling 15-25 second video scene with a spoken script.
Return ONLY valid JSON.
{{
  "duration": number,
  "language": "Tamil" or "English",
  "character": "Farmer|Doctor|Student|Businessman|Teacher|Scientist",
  "background": "Village|Farm|Hospital|School|Office|City",
  "script": "Natural spoken dialogue",
  "action": "Talk",
  "expression": "Inspiring",
  "props": [],
  "camera": "Zoom In",
  "voice": {{
    "gender": "Male" or "Female",
    "language": "Tamil" or "English"
  }}
}}
Rules:
- If language is Tamil, write the dialogue in Tamil Unicode script.
- Keep script concise, impactful (2-3 sentences).
- If preferred language '{pref_lang}' is given, use it.
- If preferred gender '{pref_gender}' is given, use it.
"""
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        result = response.choices[0].message.content.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[-1]
            if result.endswith("```"):
                result = result.rsplit("```", 1)[0]

        scene = json.loads(result.strip())
        scene["aspect_ratio"] = aspect_ratio

        # Step 2: Synthesize Voice
        audio_file = os.path.join(OUTPUT_DIR, "scene_audio.mp3")
        voice_info = scene.get("voice", {})
        create_audio(
            scene.get("script", ""),
            audio_file,
            language=voice_info.get("language", "Tamil"),
            gender=voice_info.get("gender", "Male")
        )

        # Step 3: Render Final Video with FFmpeg
        final_video_path = os.path.join(OUTPUT_DIR, "final_video.mp4")
        render_video(scene, audio_file, final_video_path)

        return jsonify({
            "success": True,
            "scene": scene,
            "audio": "scene_audio.mp3",
            "video": "final_video.mp4"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Pipeline failed: {str(e)}"
        }), 500


# --------------------------------------------------
# SERVE MEDIA & ASSETS
# --------------------------------------------------

@app.route("/video/<filename>")
def serve_video(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.route("/asset-preview/<category>/<name>")
def serve_asset_preview(category, name):
    cat_folder = "backgrounds" if category == "backgrounds" else "avatars"
    resolved_path = resolve_asset_path(cat_folder, name)
    directory = os.path.dirname(resolved_path)
    file_name = os.path.basename(resolved_path)
    return send_from_directory(directory, file_name)


# --------------------------------------------------
# RUN SERVER
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)