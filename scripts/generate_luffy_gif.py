#!/usr/bin/env python3
"""
Luffy Gear 1 to 5 (Gear 5 Max Account) Animated Visualizer
Generates an animated character GIF (luffy/luffy.gif) for Sai Dheeraj's profile.
Just like git-koi, it is a standalone animated pixel-art character (not a banner),
evolving through Gear 1 -> Gear 2 -> Gear 3 -> Gear 4 -> Gear 5 (Max Account),
complete with steam, giant fist, Haki lightning, and joyful Joyboy Sun God Nika bounce!
"""

import math, os, sys
from PIL import Image, ImageDraw

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(REPO_ROOT, "assets", "sprites")
OUTPUT_GIF = os.path.join(REPO_ROOT, "luffy", "luffy.gif")

def draw_sparkle(draw, x, y, size, color):
    """Draw a 4-point anime sparkle glint."""
    draw.line([(x - size, y), (x + size, y)], fill=color, width=2)
    draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
    s2 = max(int(size * 0.4), 1)
    draw.line([(x - s2, y - s2), (x + s2, y + s2)], fill=color, width=1)
    draw.line([(x - s2, y + s2), (x + s2, y - s2)], fill=color, width=1)

def draw_lightning(draw, start_pos, segments, color, width=2):
    """Draw crackling Haki lightning bolt."""
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

    raw_cutouts = []
    for i in range(1, 6):
        p = os.path.join(SPRITES_DIR, f"luffy_g{i}.png")
        if not os.path.exists(p):
            print(f"Error: Sprite not found at {p}", file=sys.stderr)
            sys.exit(1)
        raw_cutouts.append(Image.open(p).convert('RGBA'))

    canvas_w, canvas_h = 440, 320
    ground_y = 250
    target_h = 190

    # Scale each sprite to consistent height
    scaled_sprites = []
    for c in raw_cutouts:
        w, h = c.size
        new_w = int(target_h * (w / h))
        scaled_sprites.append(c.resize((new_w, target_h), Image.Resampling.LANCZOS))

    frames = []

    # Sequence stages: (sprite_idx, frame_count, title_text, title_color, sub_color)
    stages = [
        (0, 14, "GEAR 1: BASE", (248, 250, 252), (148, 163, 184)),
        (1, 14, "GEAR 2: JET STEAM ♨", (244, 114, 182), (251, 113, 133)),
        (2, 14, "GEAR 3: GIGANT 👊", (251, 191, 36), (245, 158, 11)),
        (3, 16, "GEAR 4: BOUNDMAN ⚔", (192, 132, 252), (225, 29, 72)),
        (4, 36, "👑 GEAR 5: SUN GOD NIKA [MAX]", (253, 224, 71), (245, 158, 11))
    ]

    for s_idx, (g_idx, count, title, color_main, color_sub) in enumerate(stages):
        spr = scaled_sprites[g_idx]
        sw, sh = spr.size
        cx = canvas_w // 2

        for f in range(count):
            img = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Stage-specific bounce and offsets
            if g_idx == 0:
                # G1: Gentle breathing idle bob
                dy = int(2.5 * math.sin(f * math.pi / 3.5))
                scale_shadow = 1.0 - dy * 0.05
            elif g_idx == 1:
                # G2: Fast vibration stance
                dy = int(1.5 * math.sin(f * math.pi * 1.5))
                scale_shadow = 1.0
            elif g_idx == 2:
                # G3: Heavy stance with small tremor
                dy = 0 if f % 4 != 0 else -1
                scale_shadow = 1.15
            elif g_idx == 3:
                # G4: Energetic Boundman rubber bounce
                dy = -abs(int(10 * math.sin(f * math.pi / 4)))
                scale_shadow = max(0.6, 1.0 + dy * 0.04)
            else:
                # G5: Joyful Joyboy rubbery cartoon bounce
                dy = -abs(int(14 * math.sin(f * math.pi / 4.5)))
                scale_shadow = max(0.5, 1.0 + dy * 0.035)

            # 1. Ground Shadow (Dark transparent ellipse)
            shadow_w = int(sw * 0.7 * scale_shadow)
            shadow_h = int(12 * scale_shadow)
            draw.ellipse([
                (cx - shadow_w // 2, ground_y - shadow_h // 2 + 5),
                (cx + shadow_w // 2, ground_y + shadow_h // 2 + 5)
            ], fill=(10, 10, 20, 140))

            # 2. Stage-specific Background VFX
            if g_idx == 1:
                # G2 Steam Vapors rising
                for i in range(5):
                    st_y = (ground_y - 20 - (f * 10 + i * 35) % 180)
                    st_x = cx + int(30 * math.sin(st_y * 0.05 + i)) + (i % 2 * 60 - 30)
                    r = 5 + (ground_y - st_y) // 25
                    alpha_puff = max(10, 160 - (ground_y - st_y))
                    draw.ellipse([st_x - r, st_y - r, st_x + r, st_y + r], fill=(255, 180, 210, alpha_puff))

            elif g_idx == 2:
                # G3 Impact lines radiating from fist (fist is on right side)
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

            elif g_idx == 3:
                # G4 Conqueror's Haki crackling bolts
                if f % 2 == 0:
                    draw_lightning(draw, (cx - 60, ground_y - sh + 40), [(15, 20), (-10, 15), (20, 25)], (225, 29, 72, 220), width=2)
                    draw_lightning(draw, (cx + 50, ground_y - sh + 50), [(-15, 18), (12, 12), (-18, 20)], (147, 51, 234, 220), width=2)

            elif g_idx == 4:
                # G5 Sun God Nika Golden Rays & White Clouds
                aura_r = int(95 + 6 * math.sin(f * math.pi / 3))
                # Golden solar glow
                draw.ellipse([
                    (cx - aura_r, ground_y - sh // 2 - aura_r // 2 + dy),
                    (cx + aura_r, ground_y - sh // 2 + aura_r // 2 + dy)
                ], fill=(253, 224, 71, 35))

                # Golden Conqueror lightning
                if f % 2 == 0:
                    draw_lightning(draw, (cx - 75, ground_y - sh + 20 + dy), [(20, 22), (-12, 15), (25, 20)], (253, 224, 71, 240), width=2)
                    draw_lightning(draw, (cx + 65, ground_y - sh + 30 + dy), [(-20, 20), (15, 15), (-20, 25)], (234, 88, 12, 240), width=2)

                # Floating Joyboy music notes / drum beats
                note_y = ground_y - sh - 15 - (f * 4) % 40 + dy
                draw.text((cx + 60, note_y), "♪", fill=(253, 224, 71, 220))
                draw.text((cx - 70, note_y + 10), "♫", fill=(255, 255, 255, 220))

            # 3. Paste Luffy Sprite
            pos_x = cx - sw // 2
            pos_y = ground_y - sh + dy
            img.alpha_composite(spr, (pos_x, pos_y))

            # G1 Straw hat sparkle
            if g_idx == 0 and (f % 6 < 3):
                draw_sparkle(draw, cx - 18, pos_y + 22, 5, (255, 255, 255, 240))

            # G5 Meat eating in second half of Gear 5
            if g_idx == 4 and f >= 18:
                meat_x = cx + 38
                meat_y = pos_y + 85
                # Bone
                draw.line([(meat_x - 14, meat_y), (meat_x + 14, meat_y)], fill=(245, 245, 245, 255), width=4)
                # Meat chunk
                draw.ellipse([meat_x - 10, meat_y - 8, meat_x + 10, meat_y + 8], fill=(160, 60, 40, 255))
                draw.ellipse([meat_x - 6, meat_y - 6, meat_x + 6, meat_y + 6], fill=(190, 80, 50, 255))
                # Cartoon bite sparkle
                if f % 4 < 2:
                    draw_sparkle(draw, meat_x + 12, meat_y - 6, 4, (255, 255, 200, 255))

            # 4. Clean Retro Title & Stage Indicator
            # Title text
            draw.text((cx, ground_y + 18), title, fill=color_main, anchor="mt")

            # Progress Track: [G1] ➔ [G2] ➔ [G3] ➔ [G4] ➔ [★ G5]
            track_y = ground_y + 40
            steps = ["G1", "G2", "G3", "G4", "G5 MAX"]
            track_w = 260
            step_gap = track_w // 4
            track_start_x = cx - track_w // 2

            for s_i, label in enumerate(steps):
                sx = track_start_x + s_i * step_gap
                # Color active up to current stage
                if s_i < g_idx:
                    c_dot = (148, 163, 184) # Completed
                    fill_dot = (51, 65, 85)
                elif s_i == g_idx:
                    c_dot = color_main # Current active stage
                    fill_dot = color_main if s_i == 4 else (15, 23, 42)
                else:
                    c_dot = (71, 85, 105) # Upcoming
                    fill_dot = (15, 23, 42)

                draw.ellipse([sx - 5, track_y - 5, sx + 5, track_y + 5], fill=fill_dot, outline=c_dot, width=1)
                # Connecting line to next
                if s_i < 4:
                    nxt_x = sx + step_gap
                    c_line = color_main if s_i < g_idx else (51, 65, 85)
                    draw.line([(sx + 6, track_y), (nxt_x - 6, track_y)], fill=c_line, width=1)

            frames.append(img)

    # Convert RGBA frames to transparent palette GIF
    p_frames = []
    for f_rgba in frames:
        alpha = f_rgba.split()[3]
        mask = Image.eval(alpha, lambda a: 255 if a <= 30 else 0)
        p_img = f_rgba.convert('RGB').convert('P', palette=Image.Palette.ADAPTIVE, colors=255)
        p_img.paste(255, mask)
        p_frames.append(p_img)

    p_frames[0].save(
        OUTPUT_GIF,
        save_all=True,
        append_images=p_frames[1:],
        optimize=True,
        duration=80,
        loop=0,
        transparency=255
    )
    print(f"Successfully generated animated Luffy companion GIF: {OUTPUT_GIF}")
    print(f"File size: {os.path.getsize(OUTPUT_GIF)} bytes ({os.path.getsize(OUTPUT_GIF)/1024:.1f} KB)")

if __name__ == "__main__":
    main()
