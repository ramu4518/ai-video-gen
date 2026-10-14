import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

METADATA_FILE = os.path.join(ASSETS_DIR, "asset_metadata.json")


def load_metadata():
    with open(METADATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def check_file(path):
    if path and os.path.exists(path):
        return path
    return None


def select_assets(scene):
    metadata = load_metadata()

    selected = {
        "avatar": None,
        "background": None,
        "props": [],
        "missing": []
    }

    # Avatar
    character = scene.get("character")

    if character in metadata["avatars"]:
        path = os.path.join(
            ASSETS_DIR,
            metadata["avatars"][character]
        )

        path = check_file(path)

        if path:
            selected["avatar"] = path
        else:
            selected["missing"].append(
                f"Avatar: {character}"
            )
    else:
        selected["missing"].append(
            f"Avatar: {character}"
        )

    # Background
    background = scene.get("background")

    if background in metadata["backgrounds"]:
        path = os.path.join(
            ASSETS_DIR,
            metadata["backgrounds"][background]
        )

        path = check_file(path)

        if path:
            selected["background"] = path
        else:
            selected["missing"].append(
                f"Background: {background}"
            )
    else:
        selected["missing"].append(
            f"Background: {background}"
        )

    # Props
    for prop in scene.get("props", []):

        if prop in metadata["props"]:
            path = os.path.join(
                ASSETS_DIR,
                metadata["props"][prop]
            )

            path = check_file(path)

            if path:
                selected["props"].append(path)
            else:
                selected["missing"].append(
                    f"Prop: {prop}"
                )
        else:
            selected["missing"].append(
                f"Prop: {prop}"
            )

    return selected