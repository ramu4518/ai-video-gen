import json
import os
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
METADATA_FILE = os.path.join(ASSETS_DIR, "asset_metadata.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Select best available font for Tamil & English
FONT_CANDIDATES = [
    "C:/Windows/Fonts/NIRMALA.TTF",
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/segoeui.ttf"
]
DEFAULT_FONT = next((f for f in FONT_CANDIDATES if os.path.exists(f)), "C:/Windows/Fonts/arial.ttf")


def wrap_text_for_subtitles(text, max_chars=36):
    words = text.strip().split()
    lines = []
    current_line = []
    current_len = 0

    for word in words:
        if current_len + len(word) + 1 > max_chars:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)
        else:
            current_line.append(word)
            current_len += len(word) + 1

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines[:3])


def resolve_asset_path(category, name, fallback_name=""):
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                meta = json.load(f)
                cat_dict = meta.get(category, {})
                if name in cat_dict:
                    p = os.path.join(ASSETS_DIR, cat_dict[name])
                    if os.path.exists(p):
                        return p
                for k, v in cat_dict.items():
                    if k.lower() == name.lower():
                        p = os.path.join(ASSETS_DIR, v)
                        if os.path.exists(p):
                            return p
        except Exception as e:
            print(f"Metadata lookup error: {e}")

    local_subfolder = "backgrounds" if category == "backgrounds" else "avatars" if category == "avatars" else "props"
    cand = os.path.join(ASSETS_DIR, local_subfolder, f"{name.lower()}.jpg")
    if os.path.exists(cand):
        return cand

    def_sub = "backgrounds" if category == "backgrounds" else "avatars"
    def_file = "village.jpg" if category == "backgrounds" else "farmer.jpg"
    return os.path.join(ASSETS_DIR, def_sub, def_file)


def create_scene(scene, audio_file=None, output_file=None):
    """
    Renders high-quality realistic AI video.
    Supports:
    1. Cinematic Hero Mode (Farmer in Field): Natural documentary style with Ken Burns zoom.
    2. Circular Presenter Badge Mode: Smooth circular avatar with NO square white boxes.
    """
    character = scene.get("character", "Farmer")
    background_name = scene.get("background", "Village")
    camera = scene.get("camera", "Zoom In")
    script = scene.get("script", "")
    aspect_ratio = scene.get("aspect_ratio", "16:9")

    # Dimensions
    is_vertical = (aspect_ratio == "9:16")
    w, h = (720, 1280) if is_vertical else (1280, 720)

    # Resolve Background & Avatar
    bg_path = resolve_asset_path("backgrounds", background_name, fallback_name="Village")
    avatar_path = resolve_asset_path("avatars", character, fallback_name="Farmer")

    audio_path = audio_file or os.path.join(OUTPUT_DIR, "scene_audio.mp3")
    final_output = output_file or os.path.join(OUTPUT_DIR, "final_video.mp4")

    # Create Subtitles Textfile
    timestamp = int(time.time() * 1000)
    sub_txt_path = os.path.join(OUTPUT_DIR, f"subtitles_{timestamp}.txt")
    wrapped_sub = wrap_text_for_subtitles(script, max_chars=32 if is_vertical else 40)
    with open(sub_txt_path, "w", encoding="utf-8") as f:
        f.write(wrapped_sub)

    font_escaped = DEFAULT_FONT.replace("\\", "/").replace(":", "\\:")
    rel_sub_path = os.path.relpath(sub_txt_path, os.getcwd()).replace("\\", "/")

    # Decide rendering style:
    # If character is Farmer and background is Village/Farm, the background IS the realistic farmer in his field!
    # This gives an ultra-realistic, documentary explainer look without any weird box!
    is_farmer_scene = (character.lower() == "farmer" and ("village" in background_name.lower() or "farm" in background_name.lower()))

    # Camera Zoom / Pan
    if camera == "Zoom Out":
        zoom_filter = f"zoompan=z='if(eq(on,1),1.15,max(zoom-0.0012,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}:fps=25"
    else:
        zoom_filter = f"zoompan=z='min(zoom+0.001,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}:fps=25"

    bg_filter = (
        f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"crop={w}:{h},{zoom_filter}[bg];"
    )

    topic_text = f"{character} • {background_name}".replace("'", "").replace(":", "")

    if is_vertical:
        sub_y = "h-220"
        title_y = 80
        title_x = "(w-text_w)/2"
        wave_w, wave_h = 360, 50
        wave_x = "(w-text_w)/2"
        wave_y = "h-290"
    else:
        sub_y = "h-110"
        title_y = 40
        title_x = 60
        wave_w, wave_h = 260, 45
        wave_x = 60
        wave_y = "h-110"

    sub_filter = (
        f"drawtext=fontfile='{font_escaped}':"
        f"textfile='{rel_sub_path}':"
        f"fontsize={28 if is_vertical else 32}:"
        f"fontcolor=white:"
        f"box=1:boxcolor=black@0.75:boxborderw=12:line_spacing=8:"
        f"x=(w-text_w)/2:y={sub_y},"
        f"drawtext=fontfile='{font_escaped}':"
        f"text='{topic_text}':"
        f"fontsize={20 if is_vertical else 22}:"
        f"fontcolor=0x00f0ff:"
        f"box=1:boxcolor=black@0.65:boxborderw=8:"
        f"x={title_x}:y={title_y}"
    )

    wave_filter = (
        f"[1:a]showwaves=s={wave_w}x{wave_h}:mode=line:colors=0x00f0ff@0.9:scale=cbrt[wave];"
    )

    if is_farmer_scene:
        # ----------------------------------------------------
        # CINEMATIC DOCUMENTARY MODE (Real Farmer in Field)
        # ----------------------------------------------------
        filter_complex = (
            bg_filter
            + wave_filter
            + f"[bg][wave]overlay={wave_x}:{wave_y}[v1];"
            + f"[v1]{sub_filter}[vout]"
        )

        command = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", bg_path,
            "-i", audio_path,
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-r", "25",
            "-c:a", "aac",
            "-shortest",
            final_output
        ]
    else:
        # ----------------------------------------------------
        # STUDIO CIRCULAR PRESENTER MODE (No Square White Boxes!)
        # ----------------------------------------------------
        av_size = 320 if is_vertical else 260
        radius = av_size // 2
        av_x = "(W-w)/2" if is_vertical else 70
        av_y = "200+sin(n/10)*4" if is_vertical else "180+sin(n/10)*4"

        avatar_filter = (
            f"[1:v]scale={av_size}:{av_size}:force_original_aspect_ratio=increase,"
            f"crop={av_size}:{av_size},"
            f"format=yuva420p,"
            f"geq=lum='p(X,Y)':a='if(lte(pow(X-{radius},2)+pow(Y-{radius},2),pow({radius-2},2)),255,0)'[avatar];"
        )

        wave_filter_pip = (
            f"[2:a]showwaves=s={av_size}x50:mode=line:colors=0x00f0ff@0.95:scale=cbrt[wave];"
        )

        wave_pip_y = "550" if is_vertical else "460"

        filter_complex = (
            bg_filter
            + avatar_filter
            + wave_filter_pip
            + f"[bg][avatar]overlay={av_x}:{av_y}[v1];"
            + f"[v1][wave]overlay={av_x}:{wave_pip_y}[v2];"
            + f"[v2]{sub_filter}[vout]"
        )

        command = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", bg_path,
            "-loop", "1", "-i", avatar_path,
            "-i", audio_path,
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "2:a",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-r", "25",
            "-c:a", "aac",
            "-shortest",
            final_output
        ]

    print("Running FFmpeg studio compositor...")
    subprocess.run(command, check=True)

    try:
        if os.path.exists(sub_txt_path):
            os.remove(sub_txt_path)
    except Exception:
        pass

    print(f"Realistic video created successfully: {final_output}")
    return final_output


if __name__ == "__main__":
    test_scene = {
        "character": "Farmer",
        "background": "Village",
        "script": "வணக்கம் நண்பர்களே! மழைநீரை சேமிப்போம், நிலத்தடி நீரை பாதுகாப்போம்.",
        "camera": "Zoom In",
        "aspect_ratio": "16:9"
    }
    create_scene(test_scene)