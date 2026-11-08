#!/usr/bin/env python3
"""
Luffy Account-Tier Animated Visualizer (like git-koi)
Renders ONLY the single Gear form earned by the user's account velocity:
- Commits < 15: Gear 1 (Base Straw Hat)
- 15 <= Commits < 30: Gear 2 (Jet Steam)
- 30 <= Commits < 45: Gear 3 (Gigant Fist)
- 45 <= Commits < 55: Gear 4 (Boundman)
- Commits >= 55: Gear 5 (Sun God Nika / Joyboy - MAX ACCOUNT)

Zero clutter, zero ghosting, zero overlapping text or banners.
Pure character animation with disposal=2 transparent frame clearance.
"""

import math, os, sys, subprocess, json
from PIL import Image, ImageDraw

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(REPO_ROOT, "assets", "sprites")
OUTPUT_GIF = os.path.join(REPO_ROOT, "luffy", "luffy.gif")

def fetch_commit_count(username="SaiDheeraj-19"):
    """Fetch total contributions from GitHub GraphQL API or fallback."""
    total = 59
    try:
        query = '''
        query {
          user(login: "%s") {
            contributionsCollection {
              contributionCalendar {
                totalContributions
              }
            }
          }
        }
        ''' % username
        cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            parsed = json.loads(res.stdout)
            val = parsed.get("data", {}).get("user", {}).get("contributionsCollection", {}).get("contributionCalendar", {}).get("totalContributions")
            if val is not None and val > 0:
                total = val
    except Exception as e:
        print(f"Using default count ({total}) due to: {e}", file=sys.stderr)
    return total

def determine_gear_stage(commits):
    """Determine the single Gear stage for the user's account."""
    if commits < 15:
        return 1
    elif commits < 30:
        return 2
    elif commits < 45:
        return 3
    elif commits < 55:
        return 4
    else:
        # 55+ Commits = Gear 5 Sun God Nika (Max Account)
        return 5

def draw_sparkle(draw, x, y, size, color):
    """Draw a 4-point anime glint."""
    draw.line([(x - size, y), (x + size, y)], fill=color, width=2)
    draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
    s2 = max(int(size * 0.4), 1)
    draw.line([(x - s2, y - s2), (x + s2, y + s2)], fill=color, width=1)
    draw.line([(x - s2, y + s2), (x + s2, y - s2)], fill=color, width=1)

def main():
    if not os.path.exists(SPRITES_DIR):
        print(f"Error: Sprites directory not found at {SPRITES_DIR}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(OUTPUT_GIF), exist_ok=True)

    commits = fetch_commit_count("SaiDheeraj-19")
    gear_lvl = determine_gear_stage(commits)
    print(f"Account commits: {commits} -> Active Gear: Gear {gear_lvl}")

    # Load ONLY the single sprite for the user's account gear
    sprite_path = os.path.join(SPRITES_DIR, f"luffy_g{gear_lvl}.png")
    if not os.path.exists(sprite_path):
        print(f"Error: Sprite not found at {sprite_path}", file=sys.stderr)
        sys.exit(1)

    spr_raw = Image.open(sprite_path).convert('RGBA')
    canvas_w, canvas_h = 420, 360
    ground_y = 295
    target_h = 240

    # Scale sprite to consistent height
    sw_orig, sh_orig = spr_raw.size
    target_w = int(target_h * (sw_orig / sh_orig))
    spr = spr_raw.resize((target_w, target_h), Image.Resampling.LANCZOS)
    sw, sh = spr.size
    cx = canvas_w // 2

    # 20 frames loop at 80ms = 1.6s smooth loop
    num_frames = 20
    frames = []

    for f in range(num_frames):
        # Create fresh blank transparent canvas for EVERY frame
        img = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Smooth Sinusoidal Joyboy Rubber Bounce
        bounce_phase = f * 2 * math.pi / num_frames
        dy = -int(14 * abs(math.sin(bounce_phase)))
        scale_shadow = max(0.65, 1.0 + dy * 0.025)

        # 1. Ground Shadow (Dark transparent ellipse expanding/contracting with bounce)
        shadow_w = int(sw * 0.72 * scale_shadow)
        shadow_h = int(14 * scale_shadow)
        draw.ellipse([
            (cx - shadow_w // 2, ground_y - shadow_h // 2 + 5),
            (cx + shadow_w // 2, ground_y + shadow_h // 2 + 5)
        ], fill=(15, 15, 25, 130))

        # 2. Conqueror's Haki Lightning Sparks (Golden & Purple)
        if f % 2 == 0:
            # Left gold spark
            draw.line([(cx - 70, ground_y - sh + 60 + dy), (cx - 50, ground_y - sh + 40 + dy)], fill=(253, 224, 71, 230), width=2)
            draw.line([(cx - 50, ground_y - sh + 40 + dy), (cx - 65, ground_y - sh + 20 + dy)], fill=(234, 88, 12, 230), width=2)
            # Right purple spark
            draw.line([(cx + 60, ground_y - sh + 70 + dy), (cx + 45, ground_y - sh + 50 + dy)], fill=(168, 85, 247, 230), width=2)
            draw.line([(cx + 45, ground_y - sh + 50 + dy), (cx + 65, ground_y - sh + 35 + dy)], fill=(253, 224, 71, 230), width=2)

        # 3. Composite Luffy Character Sprite (ONLY Gear 5)
        pos_x = cx - sw // 2
        pos_y = ground_y - sh + dy
        img.alpha_composite(spr, (pos_x, pos_y))

        # 4. Giant Meat Chomping in second half of loop (Frames 10 to 20)
        if f >= 10:
            meat_x = cx + 45
            meat_y = pos_y + 105
            # Bone
            draw.line([(meat_x - 14, meat_y), (meat_x + 14, meat_y)], fill=(240, 240, 240, 255), width=4)
            # Meat
            draw.ellipse([meat_x - 10, meat_y - 8, meat_x + 10, meat_y + 8], fill=(165, 55, 35, 255))
            draw.ellipse([meat_x - 6, meat_y - 6, meat_x + 6, meat_y + 6], fill=(195, 75, 45, 255))
            # Bite sparkles
            if f % 3 == 0:
                draw_sparkle(draw, meat_x + 12, meat_y - 4, 3, (255, 255, 200, 255))

        frames.append(img)

    # Convert frames to palette with transparency=255 and disposal=[2]*N
    p_frames = []
    for f_rgba in frames:
        alpha = f_rgba.split()[3]
        mask = Image.eval(alpha, lambda a: 255 if a <= 30 else 0)
        p_img = f_rgba.convert('RGB').convert('P', palette=Image.Palette.ADAPTIVE, colors=255)
        p_img.paste(255, mask)
        p_frames.append(p_img)

    # Save with disposal=[2]*len(p_frames) to GUARANTEE zero frame overlapping
    p_frames[0].save(
        OUTPUT_GIF,
        save_all=True,
        append_images=p_frames[1:],
        optimize=False,
        duration=80,
        loop=0,
        transparency=255,
        disposal=[2] * len(p_frames)
    )

    print(f"Successfully generated clean Luffy GIF (Gear {gear_lvl} only): {OUTPUT_GIF}")
    print(f"Total frames: {len(p_frames)}, Size: {os.path.getsize(OUTPUT_GIF)} bytes ({os.path.getsize(OUTPUT_GIF)/1024:.1f} KB)")

if __name__ == "__main__":
    main()
