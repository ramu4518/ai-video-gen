import os
import re
import urllib.parse
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
GENERATED_DIR = os.path.join(ASSETS_DIR, "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)

DEFAULT_ASSETS = {
    "background": os.path.join(ASSETS_DIR, "backgrounds", "village.jpg"),
    "avatar": os.path.join(ASSETS_DIR, "avatars", "farmer.jpg"),
    "prop": os.path.join(ASSETS_DIR, "props", "water_pot.jpg")
}


def sanitize_filename(name):
    clean = re.sub(r'[^a-zA-Z0-9_-]', '_', name.strip().lower())
    return clean[:40] or "asset"


def get_or_generate_background(name, prompt_context="", aspect_ratio="16:9"):
    """
    Looks for local background; if not found, generates a cinematic AI background.
    """
    clean_name = sanitize_filename(name)
    ar_tag = "9_16" if aspect_ratio == "9:16" else "16_9"
    target_path = os.path.join(GENERATED_DIR, f"bg_{clean_name}_{ar_tag}.jpg")

    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
        return target_path

    # Check local pre-bundled backgrounds
    local_candidates = [
        os.path.join(ASSETS_DIR, "backgrounds", f"{name.lower()}.jpg"),
        os.path.join(ASSETS_DIR, "backgrounds", f"{name.lower()}.png"),
    ]
    for cand in local_candidates:
        if os.path.exists(cand):
            return cand

    # Generate on the fly using AI image synthesis
    w, h = (720, 1280) if aspect_ratio == "9:16" else (1280, 720)
    prompt_str = f"cinematic photorealistic wide shot of {name}, {prompt_context}, 4k ultra detailed beautiful scenery, high quality photography, no text, no watermark"
    encoded_prompt = urllib.parse.quote(prompt_str)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={w}&height={h}&nologo=true&seed=42"

    print(f"Generating AI background for '{name}'...")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "AIVideoGen/2.0"}
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            content = response.read()
            if len(content) > 5000:
                with open(target_path, "wb") as f:
                    f.write(content)
                print(f"AI Background saved to {target_path}")
                return target_path
    except Exception as e:
        print(f"Notice: AI background generation failed ({e}). Using default background.")

    return DEFAULT_ASSETS["background"]


def get_or_generate_avatar(character_name, prompt_context=""):
    """
    Looks for local character avatar; if not found, generates a clean portrait avatar.
    """
    clean_name = sanitize_filename(character_name)
    target_path = os.path.join(GENERATED_DIR, f"avatar_{clean_name}.jpg")

    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
        return target_path

    # Check local pre-bundled avatars
    local_candidates = [
        os.path.join(ASSETS_DIR, "avatars", f"{character_name.lower()}.jpg"),
        os.path.join(ASSETS_DIR, "avatars", f"{character_name.lower()}.png"),
    ]
    for cand in local_candidates:
        if os.path.exists(cand):
            return cand

    # Generate portrait avatar via AI
    prompt_str = f"friendly professional portrait photo of a {character_name}, {prompt_context}, centered face, eye contact with camera, clean studio lighting, realistic photography, sharp focus"
    encoded_prompt = urllib.parse.quote(prompt_str)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true&seed=101"

    print(f"Generating AI avatar for '{character_name}'...")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "AIVideoGen/2.0"}
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            content = response.read()
            if len(content) > 5000:
                with open(target_path, "wb") as f:
                    f.write(content)
                print(f"AI Avatar saved to {target_path}")
                return target_path
    except Exception as e:
        print(f"Notice: AI avatar generation failed ({e}). Using default avatar.")

    return DEFAULT_ASSETS["avatar"]
