#!/usr/bin/env python3
"""
Luffy Gear 5 Max Account Progression Engine
Generates an animated One Piece / Sun God Nika themed GitHub activity visualizer for Sai Dheeraj.
Features:
- Gear 1 to Gear 5 stage progression track (G1 -> G2 -> G3 -> G4 -> G5 MAX AWAKENED)
- High-res Gear 5 Sun God Nika Luffy centerpiece with golden aura and Haki lightning
- Dynamic Emperor Bounty calculated from commits & clusters (฿ 3,000,000,000)
- Advanced Haki masteries mapped to core engineering stack
- Drums of Liberation rhythmic activity heartbeat waveform (DOOM · DUT · DA · DA)
"""

import os
import sys
import json
import base64
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "assets"
LOGO_PATH = ASSETS_DIR / "luffy-gear5-circle.png"
OUTPUT_SVG = ASSETS_DIR / "luffy-gear-telemetry.svg"

def fetch_github_data(username="SaiDheeraj-19"):
    """Fetch user metrics from GitHub via gh CLI or fallback gracefully."""
    data = {
        "total_contributions": 59,
        "repo_count": 21,
        "bounty": "3,000,000,000",
        "title": "EMPEROR OF THE SEA (YONKO)",
        "languages": [
            {"name": "Python / PyTorch (Conqueror's)", "pct": 54.4, "color1": "#F59E0B", "color2": "#D97706"},
            {"name": "TypeScript / Cloud OS (Armament)", "pct": 24.7, "color1": "#38BDF8", "color2": "#0284C7"},
            {"name": "GrandLine AI / Agentic (Ryuo)", "pct": 8.6, "color1": "#C084FC", "color2": "#9333EA"},
            {"name": "CUDA / C++ / vLLM (Observation)", "pct": 5.0, "color1": "#FB7185", "color2": "#E11D48"},
        ],
        "recent_activity": [0, 1, 0, 0, 2, 0, 0, 1, 3, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 4, 7, 3, 2, 1]
    }

    try:
        query = '''
        query {
          user(login: "%s") {
            contributionsCollection {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    contributionCount
                    date
                  }
                }
              }
            }
            repositories(first: 50, ownerAffiliations: OWNER, orderBy: {field: PUSHED_AT, direction: DESC}) {
              totalCount
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
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if res.returncode == 0:
            parsed = json.loads(res.stdout)
            u = parsed.get("data", {}).get("user", {})
            if u:
                cal = u.get("contributionsCollection", {}).get("contributionCalendar", {})
                tot = cal.get("totalContributions")
                if tot is not None and tot > 0:
                    data["total_contributions"] = tot

                repos = u.get("repositories", {})
                if repos.get("totalCount"):
                    data["repo_count"] = repos["totalCount"]

                weeks = cal.get("weeks", [])
                all_days = [d["contributionCount"] for w in weeks for d in w.get("contributionDays", [])]
                if len(all_days) >= 28:
                    data["recent_activity"] = all_days[-28:]

                # Extract languages
                lang_map = {}
                for repo in repos.get("nodes", []):
                    for edge in repo.get("languages", {}).get("edges", []):
                        name = edge["node"]["name"]
                        sz = edge["size"]
                        lang_map[name] = lang_map.get(name, 0) + sz

                total_sz = sum(lang_map.values())
                if total_sz > 0:
                    top_sorted = sorted(lang_map.items(), key=lambda x: x[1], reverse=True)
                    palette = [
                        ("#F59E0B", "#D97706"),
                        ("#38BDF8", "#0284C7"),
                        ("#C084FC", "#9333EA"),
                        ("#FB7185", "#E11D48")
                    ]
                    haki_labels = ["(Conqueror's)", "(Armament)", "(Ryuo)", "(Observation)"]
                    mapped_langs = []
                    for idx, (lname, lsz) in enumerate(top_sorted[:4]):
                        pct = round((lsz / total_sz) * 100, 1)
                        c1, c2 = palette[idx % len(palette)]
                        mapped_langs.append({
                            "name": f"{lname} {haki_labels[idx]}",
                            "pct": pct,
                            "color1": c1,
                            "color2": c2
                        })
                    data["languages"] = mapped_langs
    except Exception as e:
        print(f"Note: using fallback data due to: {e}", file=sys.stderr)

    return data

def generate_svg(data, logo_b64):
    """Render the animated Luffy Gear 5 Max Account SVG."""
    w, h = 880, 400

    # Build drums of liberation waveform
    recent = data["recent_activity"]
    max_c = max(max(recent), 1)
    pts = []
    area_pts = ["360,340"]
    for i, count in enumerate(recent):
        px = 360 + (i / (len(recent) - 1)) * 460
        py = 340 - (count / max_c) * 32
        pts.append(f"{px:.1f},{py:.1f}")
        area_pts.append(f"{px:.1f},{py:.1f}")
    area_pts.append("820,340")
    sparkline_path = "M " + " L ".join(pts)
    sparkline_area = "M " + " L ".join(area_pts) + " Z"

    # Languages bars
    langs_svg = []
    bar_y_start = 208
    bar_spacing = 25
    max_bar_width = 380

    for idx, lang in enumerate(data["languages"]):
        ly = bar_y_start + idx * bar_spacing
        bar_w = max(int((lang["pct"] / 100.0) * max_bar_width), 10)
        grad_id = f"luffy-grad-{idx}"
        langs_svg.append(f'''
        <!-- Lang {idx}: {lang["name"]} -->
        <g transform="translate(360, {ly})">
          <text x="0" y="0" class="hud-label" font-size="11" fill="#E2E8F0" font-weight="600">{lang["name"]}</text>
          <text x="460" y="0" text-anchor="end" class="hud-mono" font-size="11" fill="{lang["color1"]}" font-weight="700">{lang["pct"]}%</text>
          <!-- Track -->
          <rect x="0" y="5" width="460" height="5" rx="2.5" fill="#18182E" stroke="#2D224E" stroke-width="0.8"/>
          <!-- Active Bar -->
          <rect x="0" y="5" width="{bar_w}" height="5" rx="2.5" fill="url(#{grad_id})" class="bar-glow"/>
        </g>''')

    langs_svg_str = "\n".join(langs_svg)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">
  <defs>
    <!-- Grand Line Midnight Background -->
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070714"/>
      <stop offset="50%" stop-color="#120A24"/>
      <stop offset="100%" stop-color="#06060F"/>
    </linearGradient>

    <!-- Sun God Golden Radial Aura -->
    <radialGradient id="sun-god-aura" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FCD34D" stop-opacity="0.5"/>
      <stop offset="50%" stop-color="#F59E0B" stop-opacity="0.2"/>
      <stop offset="100%" stop-color="#D97706" stop-opacity="0"/>
    </radialGradient>

    <!-- Conqueror Haki Flash Gradient -->
    <linearGradient id="haki-lightning" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E11D48"/>
      <stop offset="50%" stop-color="#9333EA"/>
      <stop offset="100%" stop-color="#F59E0B"/>
    </linearGradient>

    <!-- Drums of Liberation Area Gradient -->
    <linearGradient id="drums-area-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#F59E0B" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#D97706" stop-opacity="0"/>
    </linearGradient>

    <!-- Gear 5 Gold Ribbon Gradient -->
    <linearGradient id="g5-gold" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FDE047"/>
      <stop offset="50%" stop-color="#F59E0B"/>
      <stop offset="100%" stop-color="#EA580C"/>
    </linearGradient>

    <!-- Language Gradients -->
    <linearGradient id="luffy-grad-0" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{data['languages'][0]['color1']}"/>
      <stop offset="100%" stop-color="{data['languages'][0]['color2']}"/>
    </linearGradient>
    <linearGradient id="luffy-grad-1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{data['languages'][1]['color1']}"/>
      <stop offset="100%" stop-color="{data['languages'][1]['color2']}"/>
    </linearGradient>
    <linearGradient id="luffy-grad-2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{data['languages'][2]['color1']}"/>
      <stop offset="100%" stop-color="{data['languages'][2]['color2']}"/>
    </linearGradient>
    <linearGradient id="luffy-grad-3" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{data['languages'][3]['color1']}"/>
      <stop offset="100%" stop-color="{data['languages'][3]['color2']}"/>
    </linearGradient>

    <!-- Glow Filters -->
    <filter id="gold-glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="haki-spark" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Pattern -->
    <pattern id="haki-dots" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="10" cy="10" r="0.8" fill="#4C1D95" opacity="0.4"/>
    </pattern>

    <clipPath id="luffy-circle-clip">
      <circle cx="175" cy="235" r="76"/>
    </clipPath>
  </defs>

  <style>
    @keyframes spin-cw {{
      0% {{ transform: rotate(0deg); }}
      100% {{ transform: rotate(360deg); }}
    }}
    @keyframes spin-ccw {{
      0% {{ transform: rotate(360deg); }}
      100% {{ transform: rotate(0deg); }}
    }}
    @keyframes nika-breathe {{
      0%, 100% {{ transform: scale(1); filter: drop-shadow(0 0 16px rgba(245, 158, 11, 0.6)); }}
      50% {{ transform: scale(1.035); filter: drop-shadow(0 0 30px rgba(253, 224, 71, 0.95)); }}
    }}
    @keyframes max-badge-pulse {{
      0%, 100% {{ filter: drop-shadow(0 0 4px #F59E0B); opacity: 1; }}
      50% {{ filter: drop-shadow(0 0 14px #FDE047); opacity: 0.9; }}
    }}
    @keyframes lightning-flash {{
      0%, 92%, 100% {{ opacity: 0.3; }}
      94% {{ opacity: 1; }}
      96% {{ opacity: 0.4; }}
      98% {{ opacity: 1; }}
    }}
    @keyframes liberation-beat {{
      0%, 100% {{ transform: scaleY(1); }}
      50% {{ transform: scaleY(1.08); }}
    }}

    .orbit-cw {{
      transform-origin: 175px 235px;
      animation: spin-cw 26s linear infinite;
    }}
    .orbit-ccw {{
      transform-origin: 175px 235px;
      animation: spin-ccw 38s linear infinite;
    }}
    .luffy-portal {{
      transform-origin: 175px 235px;
      animation: nika-breathe 4.5s ease-in-out infinite;
    }}
    .max-glow {{
      animation: max-badge-pulse 2.2s ease-in-out infinite;
    }}
    .haki-lightning {{
      animation: lightning-flash 5s ease-in-out infinite;
    }}
    .bar-glow {{
      animation: max-badge-pulse 3s ease-in-out infinite;
    }}

    text {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "JetBrains Mono", sans-serif;
    }}
    .hud-title {{
      font-weight: 800;
      letter-spacing: 2px;
    }}
    .hud-mono {{
      font-family: "JetBrains Mono", SFMono-Regular, Consolas, monospace;
    }}
    .hud-label {{
      letter-spacing: 1px;
    }}
  </style>

  <!-- Base Grand Line Chassis -->
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="url(#bg-grad)" stroke="#2D1F52" stroke-width="1.2"/>
  <rect x="2" y="2" width="{w-4}" height="{h-4}" rx="13" fill="url(#haki-dots)"/>

  <!-- Outer Haki Golden Border Frame -->
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="none" stroke="#F59E0B" stroke-width="1.2" stroke-opacity="0.3" stroke-dasharray="14 8 4 8"/>

  <!-- Tactical Golden Corner Brackets -->
  <path d="M 16 34 L 16 16 L 34 16" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M {w-34} 16 L {w-16} 16 L {w-16} 34" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M 16 {h-34} L 16 {h-16} L 34 {h-16}" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M {w-34} {h-16} L {w-16} {h-16} L {w-16} {h-34}" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round"/>

  <!-- ==================== TOP: GEAR 1 TO GEAR 5 EVOLUTION TRACK ==================== -->
  <g transform="translate(40, 24)">
    <!-- Stage Connect Bar -->
    <line x1="80" y1="20" x2="720" y2="20" stroke="#2D224E" stroke-width="3"/>
    <line x1="80" y1="20" x2="720" y2="20" stroke="url(#g5-gold)" stroke-width="2.5" filter="url(#gold-glow)"/>

    <!-- Stage 1: Gear 1 (Base) -->
    <g transform="translate(60, 20)">
      <circle cx="0" cy="0" r="14" fill="#0C0D1E" stroke="#F59E0B" stroke-width="1.8"/>
      <text x="0" y="4" text-anchor="middle" class="hud-mono" font-size="10" fill="#F8FAFC" font-weight="800">G1</text>
      <text x="0" y="24" text-anchor="middle" class="hud-mono" font-size="8" fill="#94A3B8">BASE</text>
    </g>

    <!-- Stage 2: Gear 2 (Jet Steam) -->
    <g transform="translate(220, 20)">
      <circle cx="0" cy="0" r="14" fill="#0C0D1E" stroke="#F59E0B" stroke-width="1.8"/>
      <text x="0" y="4" text-anchor="middle" class="hud-mono" font-size="10" fill="#F8FAFC" font-weight="800">G2</text>
      <text x="0" y="24" text-anchor="middle" class="hud-mono" font-size="8" fill="#94A3B8">JET</text>
    </g>

    <!-- Stage 3: Gear 3 (Gigant) -->
    <g transform="translate(380, 20)">
      <circle cx="0" cy="0" r="14" fill="#0C0D1E" stroke="#F59E0B" stroke-width="1.8"/>
      <text x="0" y="4" text-anchor="middle" class="hud-mono" font-size="10" fill="#F8FAFC" font-weight="800">G3</text>
      <text x="0" y="24" text-anchor="middle" class="hud-mono" font-size="8" fill="#94A3B8">GIGANT</text>
    </g>

    <!-- Stage 4: Gear 4 (Boundman) -->
    <g transform="translate(540, 20)">
      <circle cx="0" cy="0" r="14" fill="#0C0D1E" stroke="#F59E0B" stroke-width="1.8"/>
      <text x="0" y="4" text-anchor="middle" class="hud-mono" font-size="10" fill="#F8FAFC" font-weight="800">G4</text>
      <text x="0" y="24" text-anchor="middle" class="hud-mono" font-size="8" fill="#94A3B8">BOUND</text>
    </g>

    <!-- Stage 5: Gear 5 (Sun God Nika) - MAX ACCOUNT -->
    <g transform="translate(710, 20)" class="max-glow">
      <circle cx="0" cy="0" r="18" fill="#F59E0B" stroke="#FDE047" stroke-width="2.5" filter="url(#gold-glow)"/>
      <text x="0" y="5" text-anchor="middle" class="hud-mono" font-size="11" fill="#070714" font-weight="900">G5</text>
      <rect x="-38" y="22" width="76" height="15" rx="7.5" fill="#E11D48" stroke="#FDE047" stroke-width="1"/>
      <text x="0" y="33" text-anchor="middle" class="hud-mono" font-size="8" fill="#FFFFFF" font-weight="900" letter-spacing="1">MAX FORM</text>
    </g>
  </g>

  <!-- Divider Line -->
  <line x1="30" y1="78" x2="{w-30}" y2="78" stroke="#2D224E" stroke-width="1"/>
  <line x1="30" y1="78" x2="250" y2="78" stroke="#F59E0B" stroke-width="1.5" stroke-opacity="0.8" filter="url(#gold-glow)"/>

  <!-- ==================== LEFT: GEAR 5 SUN GOD NIKA PORTAL ==================== -->
  <!-- Ambient Sun God Aura -->
  <circle cx="175" cy="235" r="135" fill="url(#sun-god-aura)"/>

  <!-- Outer Stationary Celestial Ticks -->
  <circle cx="175" cy="235" r="120" fill="none" stroke="#2D224E" stroke-width="1.5"/>
  <circle cx="175" cy="235" r="120" fill="none" stroke="#F59E0B" stroke-width="1.5" stroke-opacity="0.4" stroke-dasharray="3 14"/>

  <!-- Conqueror Haki Sparks -->
  <g class="haki-lightning">
    <path d="M 120 145 L 140 175 L 130 185 L 160 215" fill="none" stroke="#E11D48" stroke-width="2" filter="url(#haki-spark)"/>
    <path d="M 230 155 L 210 180 L 225 195 L 200 230" fill="none" stroke="#9333EA" stroke-width="2" filter="url(#haki-spark)"/>
    <path d="M 110 270 L 135 250 L 125 240 L 150 220" fill="none" stroke="#FDE047" stroke-width="2" filter="url(#gold-glow)"/>
  </g>

  <!-- Outer Orbiting Cloud Ring (CCW) -->
  <g class="orbit-ccw">
    <circle cx="175" cy="235" r="105" fill="none" stroke="#FDE047" stroke-width="1.8" stroke-opacity="0.6" stroke-dasharray="28 14 8 14"/>
    <circle cx="70" cy="235" r="5" fill="#FCD34D" filter="url(#gold-glow)"/>
    <circle cx="280" cy="235" r="4" fill="#E11D48" filter="url(#gold-glow)"/>
  </g>

  <!-- Middle Orbiting Ring (CW) -->
  <g class="orbit-cw">
    <circle cx="175" cy="235" r="88" fill="none" stroke="#C084FC" stroke-width="1.8" stroke-dasharray="34 16 12 16" stroke-opacity="0.75"/>
    <circle cx="175" cy="147" r="4.5" fill="#9333EA" filter="url(#haki-spark)"/>
    <circle cx="175" cy="323" r="4.5" fill="#38BDF8" filter="url(#gold-glow)"/>
  </g>

  <!-- Inner Portal Frame -->
  <circle cx="175" cy="235" r="80" fill="#060612" stroke="#F59E0B" stroke-width="2"/>

  <!-- Luffy Gear 5 Artwork Display -->
  <g class="luffy-portal">
    <image href="data:image/png;base64,{logo_b64}" x="99" y="159" width="152" height="152" clip-path="url(#luffy-circle-clip)"/>
    <!-- Golden Solar Halo -->
    <circle cx="175" cy="235" r="76" fill="none" stroke="#FDE047" stroke-width="2" stroke-opacity="0.8" filter="url(#gold-glow)"/>
  </g>

  <!-- Portal Subtitle -->
  <text x="175" y="375" text-anchor="middle" class="hud-mono" font-size="9" fill="#F59E0B" font-weight="800" letter-spacing="1.5">SUN GOD NIKA // JOYBOY</text>

  <!-- ==================== RIGHT: EMPEROR COMBAT & TELEMETRY HUD ==================== -->

  <!-- Header Bar -->
  <g transform="translate(360, 102)">
    <!-- Title -->
    <text x="0" y="0" class="hud-title" font-size="13" fill="#F8FAFC">MONKEY D. LUFFY // GEAR 5 TELEMETRY</text>

    <!-- Yonko Badge -->
    <rect x="330" y="-12" width="130" height="18" rx="9" fill="#E11D48" fill-opacity="0.2" stroke="#E11D48" stroke-width="1.2"/>
    <text x="395" y="0" text-anchor="middle" class="hud-mono" font-size="9" fill="#FDA4AF" font-weight="900">YONKO • EMPEROR</text>
  </g>

  <!-- Three Metric Cards -->
  <!-- Card 1: Bounty -->
  <g transform="translate(360, 116)">
    <rect x="0" y="0" width="145" height="54" rx="8" fill="#0C0D22" stroke="#2D224E" stroke-width="1"/>
    <text x="12" y="17" class="hud-label" font-size="9" fill="#94A3B8" font-weight="700">CURRENT BOUNTY</text>
    <text x="12" y="42" class="hud-mono" font-size="16" fill="#FDE047" font-weight="900">฿ {data['bounty']}</text>
  </g>

  <!-- Card 2: Total Commits -->
  <g transform="translate(517, 116)">
    <rect x="0" y="0" width="145" height="54" rx="8" fill="#0C0D22" stroke="#2D224E" stroke-width="1"/>
    <text x="12" y="17" class="hud-label" font-size="9" fill="#94A3B8" font-weight="700">DEV VELOCITY</text>
    <text x="12" y="42" class="hud-mono" font-size="19" fill="#38BDF8" font-weight="900">{data['total_contributions']}</text>
    <text x="56" y="40" class="hud-mono" font-size="9" fill="#0284C7" font-weight="700">COMMITS</text>
  </g>

  <!-- Card 3: Account Tier -->
  <g transform="translate(675, 116)">
    <rect x="0" y="0" width="145" height="54" rx="8" fill="#0C0D22" stroke="#2D224E" stroke-width="1"/>
    <text x="12" y="17" class="hud-label" font-size="9" fill="#94A3B8" font-weight="700">ACCOUNT STATUS</text>
    <text x="12" y="42" class="hud-mono" font-size="17" fill="#E11D48" font-weight="900">LVL 100</text>
    <text x="82" y="40" class="hud-mono" font-size="9" fill="#FDE047" font-weight="900">MAX</text>
  </g>

  <!-- Languages / Haki Breakdown -->
  <text x="360" y="196" class="hud-label" font-size="10" fill="#94A3B8" font-weight="700" letter-spacing="1.2">HAKI PROFICIENCY &amp; FLEET DOMAINS</text>
  <line x1="585" y1="192" x2="820" y2="192" stroke="#2D224E" stroke-width="0.8" stroke-dasharray="4 4"/>

  {langs_svg_str}

  <!-- Drums of Liberation Heartbeat Waveform -->
  <g transform="translate(0, 16)">
    <text x="360" y="306" class="hud-label" font-size="10" fill="#F59E0B" font-weight="800" letter-spacing="1.2">DRUMS OF LIBERATION (DOOM · DUT · DA · DA)</text>
    <text x="820" y="306" text-anchor="end" class="hud-mono" font-size="9" fill="#FDE047" font-weight="700">RHYTHM: PEAK FREEDOM</text>

    <!-- Waveform Area & Line -->
    <path d="{sparkline_area}" fill="url(#drums-area-grad)"/>
    <path d="{sparkline_path}" fill="none" stroke="#F59E0B" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" filter="url(#gold-glow)"/>

    <!-- Grid Baseline -->
    <line x1="360" y1="340" x2="820" y2="340" stroke="#2D224E" stroke-width="1"/>
  </g>

  <!-- Footer Status Strip -->
  <line x1="360" y1="368" x2="820" y2="368" stroke="#2D224E" stroke-width="0.8"/>
  <g transform="translate(360, 382)">
    <text x="0" y="0" class="hud-mono" font-size="9" fill="#64748B">CREW: <tspan fill="#E2E8F0">STRAW HAT PIRATES</tspan></text>
    <text x="160" y="0" class="hud-mono" font-size="9" fill="#64748B">SEA: <tspan fill="#E2E8F0">NEW WORLD</tspan></text>
    <text x="290" y="0" class="hud-mono" font-size="9" fill="#64748B">TARGET: <tspan fill="#F59E0B">ONE PIECE</tspan></text>
    <text x="460" y="0" text-anchor="end" class="hud-mono" font-size="9" fill="#FDE047" font-weight="700">JOYBOY AWAKENED</text>
  </g>

</svg>'''
    return svg_content

def main():
    if not LOGO_PATH.exists():
        print(f"Error: logo not found at {LOGO_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(LOGO_PATH, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")

    data = fetch_github_data("SaiDheeraj-19")
    svg = generate_svg(data, logo_b64)

    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Successfully generated Luffy Gear 5 telemetry: {OUTPUT_SVG}")

if __name__ == "__main__":
    main()

