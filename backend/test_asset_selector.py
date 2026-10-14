from asset_selector import select_assets


scene = {
    "character": "Farmer",
    "background": "Village",
    "props": ["Water Pot", "Book"]
}

assets = select_assets(scene)

print("\nSelected Assets:")
print("Avatar:", assets["avatar"])
print("Background:", assets["background"])
print("Props:", assets["props"])

print("\nMissing Assets:")
print(assets["missing"])