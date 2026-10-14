import glob
import os
import shutil
import subprocess
import tempfile

from scene_composer import resolve_asset_path


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SADTALKER_DIR = os.path.join(BASE_DIR, "backend", "models", "SadTalker")


def is_enabled():
    return os.getenv("SADTALKER_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def render_talking_head(scene, audio_file, output_file):
    python_executable = os.getenv("SADTALKER_PYTHON", "python")
    image_size = os.getenv("SADTALKER_SIZE", "256")
    checkpoint_dir = os.path.join(SADTALKER_DIR, "checkpoints")
    required_checkpoints = (
        "auido2exp_00300-model.pth",
        "auido2pose_00140-model.pth",
        "epoch_20.pth",
        "facevid2vid_00189-model.pth.tar",
        "mapping_00229-model.pth.tar",
        "wav2lip.pth",
    )
    missing_checkpoints = [
        os.path.join(checkpoint_dir, filename)
        for filename in required_checkpoints
        if not os.path.isfile(os.path.join(checkpoint_dir, filename))
    ]
    if missing_checkpoints:
        raise FileNotFoundError(
            "SadTalker checkpoint files are missing: "
            + ", ".join(os.path.basename(path) for path in missing_checkpoints)
            + ". "
            "Download the SadTalker model checkpoints before enabling SADTALKER_ENABLED."
        )

    character = scene.get("character", "Farmer")
    avatar_path = resolve_asset_path("avatars", character, fallback_name="Farmer")
    if not os.path.isfile(avatar_path):
        raise FileNotFoundError(f"Avatar image not found: {avatar_path}")
    if not os.path.isfile(audio_file):
        raise FileNotFoundError(f"Generated audio not found: {audio_file}")

    with tempfile.TemporaryDirectory(prefix="sadtalker-") as temp_dir:
        result_dir = os.path.join(temp_dir, "results")
        os.makedirs(result_dir)
        command = [
            python_executable,
            "inference.py",
            "--source_image",
            avatar_path,
            "--driven_audio",
            audio_file,
            "--result_dir",
            result_dir,
            "--checkpoint_dir",
            os.path.join(SADTALKER_DIR, "checkpoints"),
            "--size",
            image_size,
            "--batch_size",
            "1",
            "--old_version",
        ]
        completed = subprocess.run(
            command,
            cwd=SADTALKER_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode:
            details = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"SadTalker failed (exit {completed.returncode}): {details}")

        generated_videos = glob.glob(os.path.join(result_dir, "*.mp4"))
        if len(generated_videos) != 1:
            raise RuntimeError(
                f"Expected one SadTalker output video, found {len(generated_videos)}."
            )
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        shutil.copy2(generated_videos[0], output_file)

    return output_file