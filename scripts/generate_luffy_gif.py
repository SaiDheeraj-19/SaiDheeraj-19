#!/usr/bin/env python3
"""
Luffy Gear 5 Companion Visualizer (like git-koi)
Features:
- Dynamically calculates Bounty based on account commits (e.g. ฿ 3,540,000,000)
- Meats based on repository languages:
  * Giant Python Meat (Blue glaze) held & chomped by Luffy
  * Drifting TypeScript (Cyan glaze) and Rust (Orange glaze) bone meats
  * Bottom Language Meat Legend
- Standalone animated character with disposal=2 ensuring zero ghosting / overlapping
"""

import math, os, sys, subprocess, json
from PIL import Image, ImageDraw

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(REPO_ROOT, "assets", "sprites")
OUTPUT_GIF = os.path.join(REPO_ROOT, "luffy", "luffy.gif")

def fetch_github_telemetry(username="SaiDheeraj-19"):
    """Fetch user commits and top languages from GitHub GraphQL API."""
    data = {
        "commits": 59,
        "languages": [
            ("Python", 54.4, (56, 189, 248)),
            ("TypeScript", 24.7, (96, 165, 250)),
            ("Rust", 3.9, (251, 146, 60))
        ]
    }

    try:
        query = '''
        query {
          user(login: "%s") {
            contributionsCollection {
              contributionCalendar {
                totalContributions
              }
            }
            repositories(first: 50, ownerAffiliations: OWNER, orderBy: {field: PUSHED_AT, direction: DESC}) {
              nodes {
                languages(first: 5, orderBy: {field: SIZE, direction: DESC}) {
                  edges {
                    size
                    node {
                      name
                    }
                  }
                }
              }
            }
          }
        }
        ''' % username
        cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
        if res.returncode == 0:
            parsed = json.loads(res.stdout)
            u = parsed.get("data", {}).get("user", {})
            if u:
                tot = u.get("contributionsCollection", {}).get("contributionCalendar", {}).get("totalContributions")
                if tot is not None and tot > 0:
                    data["commits"] = tot

                lang_map = {}
                for repo in u.get("repositories", {}).get("nodes", []):
                    for edge in repo.get("languages", {}).get("edges", []):
                        name = edge["node"]["name"]
                        sz = edge["size"]
                        lang_map[name] = lang_map.get(name, 0) + sz

                total_sz = sum(lang_map.values())
                if total_sz > 0:
                    top_sorted = sorted(lang_map.items(), key=lambda x: x[1], reverse=True)
                    palette = [(56, 189, 248), (96, 165, 250), (251, 146, 60)]
                    mapped = []
                    for idx, (lname, lsz) in enumerate(top_sorted[:3]):
                        pct = round((lsz / total_sz) * 100, 1)
                        c = palette[idx % len(palette)]
                        mapped.append((lname, pct, c))
                    data["languages"] = mapped
    except Exception as e:
        print(f"Using default metrics due to: {e}", file=sys.stderr)

    return data

def draw_sparkle(draw, x, y, size, color):
    """Draw a 4-point anime glint."""
    draw.line([(x - size, y), (x + size, y)], fill=color, width=2)
    draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
    s2 = max(int(size * 0.4), 1)
    draw.line([(x - s2, y - s2), (x + s2, y + s2)], fill=color, width=1)
    draw.line([(x - s2, y + s2), (x + s2, y - s2)], fill=color, width=1)

def draw_bone_meat(draw, x, y, scale=1.0, glaze_color=(56, 189, 248)):
    """Draw an authentic anime bone-in roast meat with roasted crust and language glaze."""
    bw = int(22 * scale)
    kr = max(1, int(3.5 * scale))
    # White Bone Shaft & Knobs
    draw.line([(x - bw, y), (x + bw, y)], fill=(250, 250, 250, 255), width=max(1, int(4 * scale)))
    draw.ellipse([x - bw - kr, y - kr, x - bw + kr, y + kr], fill=(250, 250, 250, 255))
    draw.ellipse([x + bw - kr, y - kr, x + bw + kr, y + kr], fill=(250, 250, 250, 255))

    # Juicy Roasted Meat Body (Rich roasted brown & amber)
    mw = int(16 * scale)
    mh = int(12 * scale)
    # Dark roasted crust
    draw.ellipse([x - mw, y - mh, x + mw, y + mh], fill=(120, 35, 20, 255))
    # Juicy roasted meat core
    draw.ellipse([x - mw + 2, y - mh + 2, x + mw - 2, y + mh - 2], fill=(180, 65, 35, 255))

    # Language Glaze Sauce Highlight (subtle appetizing glaze accent)
    gw = int(8 * scale)
    gh = int(5 * scale)
    draw.ellipse([x - gw, y - gh - 2, x + gw, y + gh - 2], fill=(*glaze_color, 200))

    # Glistening Grill Mark
    draw.line([(x - 5 * scale, y - 3 * scale), (x + 5 * scale, y - 3 * scale)], fill=(255, 240, 200, 230), width=max(1, int(1.5 * scale)))

def main():
    if not os.path.exists(SPRITES_DIR):
        print(f"Error: Sprites directory not found at {SPRITES_DIR}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(OUTPUT_GIF), exist_ok=True)

    telemetry = fetch_github_telemetry("SaiDheeraj-19")
    commits = telemetry["commits"]
    langs = telemetry["languages"]

    # Calculate commit-based Bounty
    # 59 commits -> ฿ 3,540,000,000 -
    bounty_val = commits * 60_000_000
    bounty_str = f"฿ {bounty_val:,} -"
    print(f"Commits: {commits} -> Bounty: {bounty_str}")
    print(f"Top Languages: {langs}")

    # Load Gear 5 sprite
    sprite_path = os.path.join(SPRITES_DIR, "luffy_g5.png")
    if not os.path.exists(sprite_path):
        print(f"Error: Sprite not found at {sprite_path}", file=sys.stderr)
        sys.exit(1)

    spr_raw = Image.open(sprite_path).convert('RGBA')
    canvas_w, canvas_h = 460, 390
    ground_y = 265
    target_h = 210

    # Scale sprite
    sw_orig, sh_orig = spr_raw.size
    target_w = int(target_h * (sw_orig / sh_orig))
    spr = spr_raw.resize((target_w, target_h), Image.Resampling.LANCZOS)
    sw, sh = spr.size
    cx = canvas_w // 2

    # 20 frames smooth loop
    num_frames = 20
    frames = []

    # Get language glaze colors
    color_py = langs[0][2] if len(langs) > 0 else (56, 189, 248)
    color_ts = langs[1][2] if len(langs) > 1 else (96, 165, 250)
    color_rs = langs[2][2] if len(langs) > 2 else (251, 146, 60)

    for f in range(num_frames):
        # Create fresh blank transparent canvas
        img = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Joyboy rubbery cartoon bounce
        bounce_phase = f * 2 * math.pi / num_frames
        dy = -int(12 * abs(math.sin(bounce_phase)))
        scale_shadow = max(0.68, 1.0 + dy * 0.025)

        # 1. Ground Shadow
        shadow_w = int(sw * 0.72 * scale_shadow)
        shadow_h = int(13 * scale_shadow)
        draw.ellipse([
            (cx - shadow_w // 2, ground_y - shadow_h // 2 + 5),
            (cx + shadow_w // 2, ground_y + shadow_h // 2 + 5)
        ], fill=(15, 15, 25, 130))

        # 2. Conqueror's Haki Sparks (crackling lightning)
        if f % 2 == 0:
            draw.line([(cx - 70, ground_y - sh + 60 + dy), (cx - 50, ground_y - sh + 40 + dy)], fill=(253, 224, 71, 230), width=2)
            draw.line([(cx - 50, ground_y - sh + 40 + dy), (cx - 65, ground_y - sh + 20 + dy)], fill=(234, 88, 12, 230), width=2)
            draw.line([(cx + 60, ground_y - sh + 70 + dy), (cx + 45, ground_y - sh + 50 + dy)], fill=(168, 85, 247, 230), width=2)
            draw.line([(cx + 45, ground_y - sh + 50 + dy), (cx + 65, ground_y - sh + 35 + dy)], fill=(253, 224, 71, 230), width=2)

        # 3. Composite Luffy Character Sprite
        pos_x = cx - sw // 2
        pos_y = ground_y - sh + dy
        img.alpha_composite(spr, (pos_x, pos_y))

        # 4. Giant Roast Meat (Held and chomped by Luffy)
        meat_x = cx + 42
        meat_y = pos_y + 98
        draw_bone_meat(draw, meat_x, meat_y, scale=1.35, glaze_color=color_py)

        # Cartoon bite sparkles in second half of loop (Frames 10..20)
        if f >= 10 and f % 3 == 0:
            draw_sparkle(draw, meat_x + 15, meat_y - 5, 4, (255, 255, 200, 255))
            # Musical note for Joyboy eating joy
            draw.text((meat_x + 22, meat_y - 18), "♪", fill=(253, 224, 71, 220))

        # 6. Bottom Bounty Section (Based on Commits)
        draw.text((cx, 292), "★ DEAD OR ALIVE ★", fill=(254, 240, 138), anchor="mt")
        draw.text((cx, 314), bounty_str, fill=(253, 224, 71), anchor="mt")

        # 7. Language Meat Legend (Under Bounty)
        legend_y = 346
        total_w = 340
        gap = total_w // len(langs)
        start_x = cx - total_w // 2 + 20

        for i, (lname, lpct, lcolor) in enumerate(langs):
            lx = start_x + i * gap
            draw.text((lx, legend_y), f"🍖 {lname} {lpct:.0f}%", fill=lcolor, anchor="mt")

        draw.text((cx, 372), f"DRIVEN BY {commits} COMMITS • SUN GOD NIKA", fill=(148, 163, 184), anchor="mt")

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

    print(f"Successfully generated Luffy Bounty & Meat GIF: {OUTPUT_GIF}")
    print(f"Frames: {len(p_frames)}, Size: {os.path.getsize(OUTPUT_GIF)} bytes ({os.path.getsize(OUTPUT_GIF)/1024:.1f} KB)")

if __name__ == "__main__":
    main()
