"""
Build all sprite assets and icons for Puppy & Cat Desktop Pet.
Exports:
- sprites/puppy/ (24 animation frames)
- sprites/kitten/ (24 animation frames)
- sprites/furniture/ (puppy_bed, kitten_bed, puppy_bowl, kitten_bowl, toy_ball)
- pet.ico (multi-resolution app icon)
"""
import os
import sys
from PIL import Image, ImageDraw

base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from sprite_generator_puppy import ensure_puppy_sprites, create_puppy_sprite
from sprite_generator_kitten import ensure_kitten_sprites, create_kitten_sprite
from sprite_generator_furniture import (
    create_puppy_bed_sprite,
    create_kitten_bed_sprite,
    create_puppy_bowl_sprite,
    create_kitten_bowl_sprite,
    create_toy_ball_sprite,
)


def build_furniture(target_dir: str, force: bool = False):
    os.makedirs(target_dir, exist_ok=True)
    items = {
        "puppy_bed.png": create_puppy_bed_sprite(),
        "kitten_bed.png": create_kitten_bed_sprite(),
        "puppy_bowl.png": create_puppy_bowl_sprite(),
        "kitten_bowl.png": create_kitten_bowl_sprite(),
        "toy_ball.png": create_toy_ball_sprite(),
    }
    for fn, img in items.items():
        fp = os.path.join(target_dir, fn)
        if force or not os.path.exists(fp):
            img.save(fp)
            print(f"Saved {fp}")


def build_app_icon(target_path: str):
    """Generate charming multi-resolution icon showing Puppy & Kitten together."""
    # Compose 128x128 icon with puppy on left, kitten on right, with pink heart in center
    pup = create_puppy_sprite(bob_y=0.0, tail_angle=2, tongue_out=True).resize((64, 64), Image.Resampling.NEAREST)
    kit = create_kitten_sprite(bob_y=0.0, tail_angle=-2, happy_eyes=True).resize((64, 64), Image.Resampling.NEAREST)

    icon_img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    # Soft background circle badge
    d = ImageDraw.Draw(icon_img)
    d.ellipse([4, 4, 123, 123], fill=(255, 248, 238, 255), outline=(225, 160, 80, 255), width=3)

    # Paste puppy and kitten sitting side by side
    icon_img.alpha_composite(pup, dest=(8, 38))
    icon_img.alpha_composite(kit, dest=(56, 38))

    # Floating heart between them
    d.polygon([(64, 28), (56, 18), (58, 12), (64, 17), (70, 12), (72, 18)], fill=(255, 80, 115, 255))

    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icon_img.save(target_path, format="ICO", sizes=sizes)
    print(f"Generated multi-resolution pet.ico: {target_path}")


def main():
    sprite_root = os.path.join(base_dir, "sprites")
    print("Generating Puppy sprites...")
    ensure_puppy_sprites(os.path.join(sprite_root, "puppy"), force=True)

    print("Generating Kitten sprites...")
    ensure_kitten_sprites(os.path.join(sprite_root, "kitten"), force=True)

    print("Generating Furniture sprites...")
    build_furniture(os.path.join(sprite_root, "furniture"), force=True)

    print("Generating Application Icon...")
    build_app_icon(os.path.join(base_dir, "pet.ico"))
    print("All sprite assets built successfully!")


if __name__ == "__main__":
    main()
