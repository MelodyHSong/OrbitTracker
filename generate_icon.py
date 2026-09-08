# 🪐 OrbitTracker — Multi-Resolution Icon Generator
# Author: MelodyHSong
# File Name: generate_icon.py
# Description: Generates multi-resolution .ico asset for OrbitTracker featuring
#              an orbital ring, planetary core, and celestial tracking satellite.

import os
import sys
import math

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("[!] Pillow is not installed. Please install it with: pip install pillow")
    sys.exit(1)


def create_orbital_icon(output_path):
    """Synthesizes a multi-resolution Windows .ico file with orbital workstation branding."""
    sizes = [(256, 256), (48, 48), (32, 32), (16, 16)]
    images = []

    for width, height in sizes:
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        s = width / 256.0

        # Background rounded badge: Deep space obsidian (#0d1117)
        pad = max(1, int(8 * s))
        corner_radius = max(3, int(46 * s))
        badge_box = [pad, pad, width - pad, height - pad]
        draw.rounded_rectangle(
            badge_box,
            radius=corner_radius,
            fill=(13, 17, 23, 255),
            outline=(88, 166, 255, 255),  # Starlight Cyan border
            width=max(1, int(7 * s))
        )

        # Inner card frame (#161b22)
        inner_pad = max(2, int(26 * s))
        inner_box = [inner_pad, inner_pad, width - inner_pad, height - inner_pad]
        draw.rounded_rectangle(
            inner_box,
            radius=max(2, int(24 * s)),
            fill=(22, 27, 34, 255),
            outline=(48, 54, 61, 255),   # Rim border
            width=max(1, int(3 * s))
        )

        # Center point
        cx = width / 2.0
        cy = height / 2.0

        # 1. Tilted Orbital Ring (Back arc)
        rx = 78 * s
        ry = 32 * s
        ring_bbox = [cx - rx, cy - ry, cx + rx, cy + ry]
        draw.arc(ring_bbox, start=180, end=360, fill=(88, 166, 255, 120), width=max(1, int(5 * s)))

        # 2. Planetary Celestial Core (Gradient / shaded sphere)
        core_r = 42 * s
        # Atmospheric glow
        draw.ellipse([cx - core_r - 6 * s, cy - core_r - 6 * s, cx + core_r + 6 * s, cy + core_r + 6 * s],
                     fill=(88, 166, 255, 40))
        # Planet body
        draw.ellipse([cx - core_r, cy - core_r, cx + core_r, cy + core_r],
                     fill=(33, 38, 45, 255),
                     outline=(242, 204, 96, 255),  # Golden corona
                     width=max(1, int(4 * s)))

        # Inner core highlight
        inner_r = 20 * s
        draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                     fill=(88, 166, 255, 220))

        # 3. Tilted Orbital Ring (Front arc)
        draw.arc(ring_bbox, start=0, end=180, fill=(88, 166, 255, 255), width=max(1, int(6 * s)))

        # 4. Tracking Satellite Node on the orbit
        sat_angle = math.radians(35)
        sat_x = cx + rx * math.cos(sat_angle)
        sat_y = cy + ry * math.sin(sat_angle)
        sat_r = max(2, int(9 * s))
        # Satellite outer glow
        draw.ellipse([sat_x - sat_r - 2 * s, sat_y - sat_r - 2 * s, sat_x + sat_r + 2 * s, sat_y + sat_r + 2 * s],
                     fill=(242, 204, 96, 160))
        # Satellite core
        draw.ellipse([sat_x - sat_r, sat_y - sat_r, sat_x + sat_r, sat_y + sat_r],
                     fill=(242, 204, 96, 255),
                     outline=(255, 255, 255, 255),
                     width=max(1, int(2 * s)))

        # Small status spark
        if width >= 48:
            sp_x = cx - int(56 * s)
            sp_y = cy - int(52 * s)
            sp_r = int(5 * s)
            draw.ellipse([sp_x - sp_r, sp_y - sp_r, sp_x + sp_r, sp_y + sp_r], fill=(126, 231, 135, 240))

        images.append(img)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    images[0].save(
        output_path,
        format="ICO",
        sizes=[(im.width, im.height) for im in images],
        append_images=images[1:]
    )
    print(f"[✓] Successfully generated OrbitTracker multi-resolution icon at:\n    {output_path}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    output_ico = os.path.join(assets_dir, "app_icon.ico")
    create_orbital_icon(output_ico)


if __name__ == "__main__":
    main()
