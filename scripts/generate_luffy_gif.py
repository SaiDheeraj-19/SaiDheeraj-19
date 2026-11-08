#!/usr/bin/env python3
"""
Luffy Account-Tier Activity Visualizer (like git-koi)
Determines Luffy's Gear stage based on the user's actual GitHub contribution count:
- Commits < 15: Gear 1 (Base Straw Hat)
- 15 <= Commits < 30: Gear 2 (Jet Steam)
- 30 <= Commits < 45: Gear 3 (Gigant Fist)
- 45 <= Commits < 55: Gear 4 (Boundman)
- Commits >= 55: Gear 5 (Sun God Nika / Joyboy - MAX ACCOUNT)

Features:
- Standalone animated character companion GIF (luffy/luffy.gif)
- disposal=2 on every frame ensuring 100% clean transparent rendering with ZERO overlapping
- Animated breathing, cartoon bounce, Haki lightning, and Drums of Liberation rhythm
- Gear progression tracker showing unlocked stages
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
    """Determine Gear 1..5 based on account commit velocity."""
    if commits < 15:
        return 1, "GEAR 1: BASE STRAW HAT", (248, 250, 252), (148, 163, 184)
    elif commits < 30:
        return 2, "GEAR 2: JET STEAM ♨", (244, 114, 182), (251, 113, 133)
    elif commits < 45:
        return 3, "GEAR 3: GIGANT 👊", (251, 191, 36), (245, 158, 11)
    elif commits < 55:
        return 4, "GEAR 4: BOUNDMAN ⚔", (192, 132, 252), (225, 29, 72)
    else:
        # 55+ Commits = Gear 5 Sun God Nika (Max Account)
        return 5, "👑 GEAR 5: SUN GOD NIKA [MAX ACCOUNT]", (253, 224, 71), (245, 158, 11)

def draw_sparkle(draw, x, y, size, color):
    """Draw a 4-point anime glint."""
    draw.line([(x - size, y), (x + size, y)], fill=color, width=2)
    draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
    s2 = max(int(size * 0.4), 1)
    draw.line([(x - s2, y - s2), (x + s2, y + s2)], fill=color, width=1)
    draw.line([(x - s2, y + s2), (x + s2, y - s2)], fill=color, width=1)

def draw_lightning(draw, start_pos, segments, color, width=2):
    """Draw crackling Conqueror's Haki lightning."""
    cur = start_pos
    for dx, dy in segments:
        nxt = (cur[0] + dx, cur[1] + dy)
        draw.line([cur, nxt], fill=color, width=width)
        cur = nxt

def main():
    if not os.path.exists(SPRITES_DIR):
        print(f"Error: Sprites directory not found at {SPRITES_DIR}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(OUTPUT_GIF), exist_ok=True)

    commits = fetch_commit_count("SaiDheeraj-19")
    gear_lvl, title, color_main, color_sub = determine_gear_stage(commits)
    print(f"Account commits: {commits} -> Level: Gear {gear_lvl} ({title})")

    sprite_path = os.path.join(SPRITES_DIR, f"luffy_g{gear_lvl}.png")
    if not os.path.exists(sprite_path):
        print(f"Error: Sprite not found at {sprite_path}", file=sys.stderr)
        sys.exit(1)

    spr_raw = Image.open(sprite_path).convert('RGBA')
    canvas_w, canvas_h = 440, 320
    ground_y = 250
    target_h = 190

    # Scale sprite cleanly
    sw_orig, sh_orig = spr_raw.size
    target_w = int(target_h * (sw_orig / sh_orig))
    spr = spr_raw.resize((target_w, target_h), Image.Resampling.LANCZOS)
    sw, sh = spr.size
    cx = canvas_w // 2

    # Animation loop: 24 frames at 80ms = ~1.9s smooth loop
    num_frames = 24
    frames = []

    for f in range(num_frames):
        # Create fresh blank transparent canvas for every frame
        img = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Gear-specific motion parameters
        if gear_lvl == 1:
            dy = int(3 * math.sin(f * 2 * math.pi / num_frames))
            scale_shadow = 1.0 - (dy * 0.04)
        elif gear_lvl == 2:
            dy = int(2 * math.sin(f * 4 * math.pi / num_frames))
            scale_shadow = 1.0
        elif gear_lvl == 3:
            dy = 0 if f % 3 != 0 else -1
            scale_shadow = 1.15
        elif gear_lvl == 4:
            dy = -abs(int(10 * math.sin(f * 2 * math.pi / num_frames)))
            scale_shadow = max(0.6, 1.0 + dy * 0.04)
        else:
            # Gear 5: Joyboy rubbery cartoon bounce
            dy = -abs(int(14 * math.sin(f * 2 * math.pi / num_frames)))
            scale_shadow = max(0.55, 1.0 + dy * 0.035)

        # 1. Ground Shadow (Dark transparent ellipse with breathing scale)
        shadow_w = int(sw * 0.72 * scale_shadow)
        shadow_h = int(12 * scale_shadow)
        draw.ellipse([
            (cx - shadow_w // 2, ground_y - shadow_h // 2 + 5),
            (cx + shadow_w // 2, ground_y + shadow_h // 2 + 5)
        ], fill=(10, 10, 20, 140))

        # 2. Stage-Specific Background VFX
        if gear_lvl == 2:
            # G2 Rising Steam Plumes
            for i in range(5):
                st_y = (ground_y - 20 - (f * 10 + i * 35) % 180)
                st_x = cx + int(30 * math.sin(st_y * 0.05 + i)) + (i % 2 * 60 - 30)
                r = 5 + (ground_y - st_y) // 25
                alpha_puff = max(10, 160 - (ground_y - st_y))
                draw.ellipse([st_x - r, st_y - r, st_x + r, st_y + r], fill=(255, 180, 210, alpha_puff))

        elif gear_lvl == 3:
            # G3 Giant Fist Impact Lines
            fist_x = cx + sw // 2 - 20
            fist_y = ground_y - sh // 2
            if f % 3 == 0:
                for ang in [0, 45, -45, 90, -90]:
                    rad = math.radians(ang)
                    x1 = fist_x + int(45 * math.cos(rad))
                    y1 = fist_y + int(45 * math.sin(rad))
                    x2 = fist_x + int(70 * math.cos(rad))
                    y2 = fist_y + int(70 * math.sin(rad))
                    draw.line([(x1, y1), (x2, y2)], fill=(255, 215, 0, 180), width=2)

        elif gear_lvl == 4:
            # G4 Conqueror's Haki Lightning
            if f % 2 == 0:
                draw_lightning(draw, (cx - 60, ground_y - sh + 40), [(15, 20), (-10, 15), (20, 25)], (225, 29, 72, 220), width=2)
                draw_lightning(draw, (cx + 50, ground_y - sh + 50), [(-15, 18), (12, 12), (-18, 20)], (147, 51, 234, 220), width=2)

        elif gear_lvl == 5:
            # G5 Sun God Nika Golden Rays & Floating Clouds
            aura_r = int(95 + 6 * math.sin(f * 2 * math.pi / num_frames))
            draw.ellipse([
                (cx - aura_r, ground_y - sh // 2 - aura_r // 2 + dy),
                (cx + aura_r, ground_y - sh // 2 + aura_r // 2 + dy)
            ], fill=(253, 224, 71, 35))

            # Golden & Purple Conqueror's Haki Lightning
            if f % 2 == 0:
                draw_lightning(draw, (cx - 75, ground_y - sh + 20 + dy), [(20, 22), (-12, 15), (25, 20)], (253, 224, 71, 240), width=2)
                draw_lightning(draw, (cx + 65, ground_y - sh + 30 + dy), [(-20, 20), (15, 15), (-20, 25)], (234, 88, 12, 240), width=2)

            # Floating Drums of Liberation Musical Notes
            note_y = ground_y - sh - 15 - (f * 5) % 40 + dy
            draw.text((cx + 60, note_y), "♪", fill=(253, 224, 71, 220))
            draw.text((cx - 70, note_y + 10), "♫", fill=(255, 255, 255, 220))

        # 3. Composite Luffy Character Sprite
        pos_x = cx - sw // 2
        pos_y = ground_y - sh + dy
        img.alpha_composite(spr, (pos_x, pos_y))

        # G1 Straw Hat Sparkle
        if gear_lvl == 1 and (f % 6 < 3):
            draw_sparkle(draw, cx - 18, pos_y + 22, 5, (255, 255, 255, 240))

        # G5 Giant Meat Chomping (Frames 12 to 24)
        if gear_lvl == 5 and f >= 12:
            meat_x = cx + 38
            meat_y = pos_y + 85
            # Bone
            draw.line([(meat_x - 14, meat_y), (meat_x + 14, meat_y)], fill=(245, 245, 245, 255), width=4)
            # Meat chunk
            draw.ellipse([meat_x - 10, meat_y - 8, meat_x + 10, meat_y + 8], fill=(160, 60, 40, 255))
            draw.ellipse([meat_x - 6, meat_y - 6, meat_x + 6, meat_y + 6], fill=(190, 80, 50, 255))
            if f % 4 < 2:
                draw_sparkle(draw, meat_x + 12, meat_y - 6, 4, (255, 255, 200, 255))

        # 4. Clean Retro Title & Gear Progression Track
        draw.text((cx, ground_y + 18), title, fill=color_main, anchor="mt")

        # Evolution Track: [G1] ➔ [G2] ➔ [G3] ➔ [G4] ➔ [★ G5 MAX]
        track_y = ground_y + 40
        steps = ["G1", "G2", "G3", "G4", "G5 MAX"]
        track_w = 260
        step_gap = track_w // 4
        track_start_x = cx - track_w // 2

        for s_i, label in enumerate(steps):
            sx = track_start_x + s_i * step_gap
            stage_num = s_i + 1
            if stage_num < gear_lvl:
                # Unlocked previous gear
                c_dot = (148, 163, 184)
                fill_dot = (51, 65, 85)
            elif stage_num == gear_lvl:
                # Current active account gear
                c_dot = color_main
                fill_dot = color_main if stage_num == 5 else (15, 23, 42)
            else:
                # Future locked gear
                c_dot = (71, 85, 105)
                fill_dot = (15, 23, 42)

            draw.ellipse([sx - 5, track_y - 5, sx + 5, track_y + 5], fill=fill_dot, outline=c_dot, width=1)
            if s_i < 4:
                nxt_x = sx + step_gap
                c_line = color_main if (s_i + 1) < gear_lvl else (51, 65, 85)
                draw.line([(sx + 6, track_y), (nxt_x - 6, track_y)], fill=c_line, width=1)

        frames.append(img)

    # Convert frames to palette with transparency=255 and disposal=[2]*N
    p_frames = []
    for f_rgba in frames:
        alpha = f_rgba.split()[3]
        mask = Image.eval(alpha, lambda a: 255 if a <= 30 else 0)
        p_img = f_rgba.convert('RGB').convert('P', palette=Image.Palette.ADAPTIVE, colors=255)
        p_img.paste(255, mask)
        p_frames.append(p_img)

    # Save with disposal=[2]*len(p_frames) to GUARANTEE zero frame overlapping!
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

    print(f"Successfully generated clean animated Luffy GIF: {OUTPUT_GIF}")
    print(f"Total frames: {len(p_frames)}, Size: {os.path.getsize(OUTPUT_GIF)} bytes ({os.path.getsize(OUTPUT_GIF)/1024:.1f} KB)")

if __name__ == "__main__":
    main()
