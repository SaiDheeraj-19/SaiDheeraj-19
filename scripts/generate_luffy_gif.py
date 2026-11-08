#!/usr/bin/env python3
"""
Luffy Gear 5 Companion Visualizer (like git-koi)
Features:
- Dynamically calculates Bounty based on account commits (e.g. ฿ 3,540,000,000)
- Language telemetry derived purely from owned/original repositories (excluding forks)
- Sun God Nika awakening with Joyboy bounce & Conqueror's Haki lightning
- Standalone animated character with disposal=2 ensuring zero ghosting / overlapping
"""

import math, os, sys, subprocess, json
from PIL import Image, ImageDraw

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(REPO_ROOT, "assets", "sprites")
OUTPUT_GIF = os.path.join(REPO_ROOT, "luffy", "luffy.gif")

# Primary language brand colors
LANG_COLORS = {
    "TypeScript": (96, 165, 250),   # #60a5fa
    "JavaScript": (250, 204, 21),   # #facc15
    "Python": (56, 189, 248),       # #38bdf8
    "Rust": (251, 146, 60),         # #fb923c
    "Go": (56, 189, 248),
    "HTML": (248, 113, 113),
    "CSS": (167, 139, 250),
}

def fetch_github_telemetry(username="SaiDheeraj-19"):
    """Fetch user commits and top languages from GitHub GraphQL API, excluding forks."""
    data = {
        "commits": 59,
        "languages": [
            ("TypeScript", 66.7, (96, 165, 250)),
            ("JavaScript", 23.3, (250, 204, 21)),
            ("Python", 3.3, (56, 189, 248))
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
            repositories(first: 50, ownerAffiliations: OWNER, isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
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
                    mapped = []
                    fallback_palette = [(96, 165, 250), (250, 204, 21), (56, 189, 248), (251, 146, 60)]
                    for idx, (lname, lsz) in enumerate(top_sorted[:3]):
                        pct = round((lsz / total_sz) * 100, 1)
                        c = LANG_COLORS.get(lname, fallback_palette[idx % len(fallback_palette)])
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

        # 3. Sun God Awakening Glints (Joyful aura)
        if f % 3 == 0:
            draw_sparkle(draw, cx - 60, ground_y - sh + 30 + dy, 4, (254, 240, 138, 240))
        elif f % 3 == 1:
            draw_sparkle(draw, cx + 62, ground_y - sh + 25 + dy, 4, (253, 224, 71, 240))

        # 4. Composite Luffy Character Sprite (Pure Sun God Nika)
        pos_x = cx - sw // 2
        pos_y = ground_y - sh + dy
        img.alpha_composite(spr, (pos_x, pos_y))

        # 5. Bottom Bounty Section (Based on Commits)
        draw.text((cx, 292), "★ DEAD OR ALIVE ★", fill=(254, 240, 138), anchor="mt")
        draw.text((cx, 314), bounty_str, fill=(253, 224, 71), anchor="mt")

        # 6. Language Breakdown (Under Bounty, clean indicator dots)
        legend_y = 346
        total_w = 340
        gap = total_w // len(langs)
        start_x = cx - total_w // 2 + 15

        for i, (lname, lpct, lcolor) in enumerate(langs):
            lx = start_x + i * gap
            # Colored language indicator dot
            draw.ellipse([lx, legend_y + 3, lx + 7, legend_y + 10], fill=lcolor)
            # Language name & percentage
            draw.text((lx + 12, legend_y), f"{lname} {lpct:.0f}%", fill=lcolor, anchor="lt")

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
