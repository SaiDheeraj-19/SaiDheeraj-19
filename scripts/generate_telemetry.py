#!/usr/bin/env python3
"""
Kairo Telemetry Kernel Visualizer
Generates an animated high-tech SVG telemetry visualizer for Kairo Technologies and Sai Dheeraj.
Features:
- Official Kairo 3D glass glowing emblem at the reactor core
- Concentric rotating orbital rings & HUD calibration marks
- Orbiting satellite data nodes (Cloud OS, Orbit AI, vLLM, PAIR)
- Real-time GitHub commit momentum, repository counts, and stack distribution
- Dynamic 28-day activity velocity sparkline/waveform
- Standalone self-contained SVG with embedded assets and CSS keyframe animations
"""

import os
import sys
import json
import base64
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "assets"
LOGO_PATH = ASSETS_DIR / "kairo-logo-256.png"
OUTPUT_SVG = ASSETS_DIR / "kairo-telemetry.svg"

def fetch_github_data(username="SaiDheeraj-19"):
    """Fetch user metrics from GitHub via gh CLI or fallback gracefully."""
    data = {
        "total_contributions": 59,
        "repo_count": 21,
        "uptime": "99.94%",
        "languages": [
            {"name": "Python / PyTorch", "pct": 54.4, "color1": "#38BDF8", "color2": "#0284C7"},
            {"name": "TypeScript / OS", "pct": 24.7, "color1": "#60A5FA", "color2": "#2563EB"},
            {"name": "Rust / Systems", "pct": 8.6, "color1": "#FB923C", "color2": "#EA580C"},
            {"name": "CUDA / C++ / vLLM", "pct": 5.0, "color1": "#C084FC", "color2": "#9333EA"},
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
                      color
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

                # Extract last 28 days
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
                    mapped_langs = []
                    palette = [
                        ("#38BDF8", "#0284C7"),
                        ("#60A5FA", "#2563EB"),
                        ("#FB923C", "#EA580C"),
                        ("#C084FC", "#9333EA")
                    ]
                    for idx, (lname, lsz) in enumerate(top_sorted[:4]):
                        pct = round((lsz / total_sz) * 100, 1)
                        c1, c2 = palette[idx % len(palette)]
                        mapped_langs.append({
                            "name": lname,
                            "pct": pct,
                            "color1": c1,
                            "color2": c2
                        })
                    data["languages"] = mapped_langs
    except Exception as e:
        print(f"Note: using fallback data due to: {e}", file=sys.stderr)

    return data

def generate_svg(data, logo_b64):
    """Render the animated cyberdeck telemetry SVG."""
    w, h = 880, 340

    # Build sparkline points
    recent = data["recent_activity"]
    # Normalizing 28 points across width 460 (from x=360 to x=820), baseline y=285, max height 32px (y=253)
    max_c = max(max(recent), 1)
    pts = []
    area_pts = ["360,285"]
    for i, count in enumerate(recent):
        px = 360 + (i / (len(recent) - 1)) * 460
        py = 285 - (count / max_c) * 28
        pts.append(f"{px:.1f},{py:.1f}")
        area_pts.append(f"{px:.1f},{py:.1f}")
    area_pts.append("820,285")
    sparkline_path = "M " + " L ".join(pts)
    sparkline_area = "M " + " L ".join(area_pts) + " Z"

    # Languages bars
    langs_svg = []
    bar_y_start = 148
    bar_spacing = 25
    max_bar_width = 380

    for idx, lang in enumerate(data["languages"]):
        ly = bar_y_start + idx * bar_spacing
        bar_w = max(int((lang["pct"] / 100.0) * max_bar_width), 8)
        grad_id = f"lang-grad-{idx}"
        langs_svg.append(f'''
        <!-- Lang {idx}: {lang["name"]} -->
        <g transform="translate(360, {ly})">
          <text x="0" y="0" class="hud-label" font-size="11" fill="#CBD5E1" font-weight="600">{lang["name"]}</text>
          <text x="460" y="0" text-anchor="end" class="hud-mono" font-size="11" fill="{lang["color1"]}" font-weight="700">{lang["pct"]}%</text>
          <!-- Track -->
          <rect x="0" y="5" width="460" height="5" rx="2.5" fill="#0F172A" stroke="#1E293B" stroke-width="0.8"/>
          <!-- Active Bar -->
          <rect x="0" y="5" width="{bar_w}" height="5" rx="2.5" fill="url(#{grad_id})" class="bar-pulse"/>
        </g>''')

    langs_svg_str = "\n".join(langs_svg)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">
  <defs>
    <!-- Background Gradient -->
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#02040A"/>
      <stop offset="45%" stop-color="#050B18"/>
      <stop offset="100%" stop-color="#02050E"/>
    </linearGradient>

    <!-- Core Blue Radial Aura -->
    <radialGradient id="reactor-aura" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#0070F3" stop-opacity="0.45"/>
      <stop offset="50%" stop-color="#00C2FF" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#0070F3" stop-opacity="0"/>
    </radialGradient>

    <!-- Radar Sweep Gradient -->
    <linearGradient id="radar-beam" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00F0FF" stop-opacity="0.55"/>
      <stop offset="60%" stop-color="#0070F3" stop-opacity="0.1"/>
      <stop offset="100%" stop-color="#0070F3" stop-opacity="0"/>
    </linearGradient>

    <!-- Sparkline Gradient Area -->
    <linearGradient id="sparkline-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#00F0FF" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#0070F3" stop-opacity="0.0"/>
    </linearGradient>

    <!-- Language Gradients -->
    <linearGradient id="lang-grad-0" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{data['languages'][0]['color1']}"/>
      <stop offset="100%" stop-color="{data['languages'][0]['color2']}"/>
    </linearGradient>
    <linearGradient id="lang-grad-1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{data['languages'][1]['color1']}"/>
      <stop offset="100%" stop-color="{data['languages'][1]['color2']}"/>
    </linearGradient>
    <linearGradient id="lang-grad-2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{data['languages'][2]['color1']}"/>
      <stop offset="100%" stop-color="{data['languages'][2]['color2']}"/>
    </linearGradient>
    <linearGradient id="lang-grad-3" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{data['languages'][3]['color1']}"/>
      <stop offset="100%" stop-color="{data['languages'][3]['color2']}"/>
    </linearGradient>

    <!-- Glow Filter -->
    <filter id="neon-glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="subtle-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Grid Pattern -->
    <pattern id="grid-dots" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="12" cy="12" r="0.8" fill="#1E293B" opacity="0.4"/>
    </pattern>

    <clipPath id="logo-circle-clip">
      <circle cx="175" cy="170" r="62"/>
    </clipPath>
  </defs>

  <style>
    @keyframes spin-clockwise {{
      0% {{ transform: rotate(0deg); }}
      100% {{ transform: rotate(360deg); }}
    }}
    @keyframes spin-counter {{
      0% {{ transform: rotate(360deg); }}
      100% {{ transform: rotate(0deg); }}
    }}
    @keyframes core-breathe {{
      0%, 100% {{ transform: scale(1); filter: drop-shadow(0 0 16px rgba(0, 112, 243, 0.65)); }}
      50% {{ transform: scale(1.035); filter: drop-shadow(0 0 28px rgba(0, 240, 255, 0.95)); }}
    }}
    @keyframes radar-scan {{
      0% {{ transform: rotate(0deg); }}
      100% {{ transform: rotate(360deg); }}
    }}
    @keyframes pulse-led {{
      0%, 100% {{ opacity: 1; filter: drop-shadow(0 0 6px #10B981); }}
      50% {{ opacity: 0.35; filter: none; }}
    }}
    @keyframes bar-shine {{
      0%, 100% {{ opacity: 0.9; }}
      50% {{ opacity: 1; filter: drop-shadow(0 0 6px rgba(0, 240, 255, 0.6)); }}
    }}
    @keyframes scanline-anim {{
      0% {{ transform: translateY(0); opacity: 0; }}
      20% {{ opacity: 0.6; }}
      80% {{ opacity: 0.6; }}
      100% {{ transform: translateY(340px); opacity: 0; }}
    }}

    .orbit-cw {{
      transform-origin: 175px 170px;
      animation: spin-clockwise 24s linear infinite;
    }}
    .orbit-ccw {{
      transform-origin: 175px 170px;
      animation: spin-counter 36s linear infinite;
    }}
    .radar-sweep {{
      transform-origin: 175px 170px;
      animation: radar-scan 6s linear infinite;
    }}
    .core-reactor {{
      transform-origin: 175px 170px;
      animation: core-breathe 4.5s ease-in-out infinite;
    }}
    .led-live {{
      animation: pulse-led 2s ease-in-out infinite;
    }}
    .bar-pulse {{
      animation: bar-shine 3s ease-in-out infinite;
    }}

    text {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "JetBrains Mono", monospace;
    }}
    .hud-title {{
      font-weight: 800;
      letter-spacing: 2.2px;
    }}
    .hud-mono {{
      font-family: "JetBrains Mono", SFMono-Regular, Consolas, monospace;
    }}
    .hud-label {{
      letter-spacing: 1px;
    }}
  </style>

  <!-- Base Chassis -->
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="url(#bg-grad)" stroke="#1E293B" stroke-width="1.2"/>
  <rect x="2" y="2" width="{w-4}" height="{h-4}" rx="13" fill="url(#grid-dots)"/>

  <!-- Outer Neon Border Frame -->
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="none" stroke="#0070F3" stroke-width="1.2" stroke-opacity="0.3" stroke-dasharray="16 10 4 10"/>

  <!-- Tactical HUD Corner Brackets -->
  <path d="M 16 34 L 16 16 L 34 16" fill="none" stroke="#38BDF8" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M {w-34} 16 L {w-16} 16 L {w-16} 34" fill="none" stroke="#38BDF8" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M 16 {h-34} L 16 {h-16} L 34 {h-16}" fill="none" stroke="#38BDF8" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M {w-34} {h-16} L {w-16} {h-16} L {w-16} {h-34}" fill="none" stroke="#38BDF8" stroke-width="2.5" stroke-linecap="round"/>

  <!-- ==================== LEFT: KAIRO ORBITAL REACTOR ==================== -->
  <!-- Ambient Backlight Glow -->
  <circle cx="175" cy="170" r="140" fill="url(#reactor-aura)"/>

  <!-- Outer Stationary Telemetry Calibrations -->
  <circle cx="175" cy="170" r="128" fill="none" stroke="#0F172A" stroke-width="1.5"/>
  <circle cx="175" cy="170" r="128" fill="none" stroke="#0070F3" stroke-width="1.5" stroke-opacity="0.4" stroke-dasharray="2 12"/>

  <!-- Degree Marks at 0, 90, 180, 270 -->
  <text x="175" y="32" text-anchor="middle" class="hud-mono" font-size="8" fill="#38BDF8" opacity="0.7">000°</text>
  <text x="312" y="173" text-anchor="middle" class="hud-mono" font-size="8" fill="#38BDF8" opacity="0.7">090°</text>
  <text x="175" y="312" text-anchor="middle" class="hud-mono" font-size="8" fill="#38BDF8" opacity="0.7">180°</text>
  <text x="38" y="173" text-anchor="middle" class="hud-mono" font-size="8" fill="#38BDF8" opacity="0.7">270°</text>

  <!-- Crosshair Reticles -->
  <line x1="175" y1="46" x2="175" y2="58" stroke="#00F0FF" stroke-width="1.5" opacity="0.7"/>
  <line x1="175" y1="282" x2="175" y2="294" stroke="#00F0FF" stroke-width="1.5" opacity="0.7"/>
  <line x1="51" y1="170" x2="63" y2="170" stroke="#00F0FF" stroke-width="1.5" opacity="0.7"/>
  <line x1="287" y1="170" x2="299" y2="170" stroke="#00F0FF" stroke-width="1.5" opacity="0.7"/>

  <!-- Outer Orbiting Ring (CCW) -->
  <g class="orbit-ccw">
    <circle cx="175" cy="170" r="114" fill="none" stroke="#38BDF8" stroke-width="1.5" stroke-opacity="0.6" stroke-dasharray="24 16 8 16"/>
    <!-- Outer Satellite 1: CLOUD OS -->
    <g transform="translate(175, 56)">
      <circle cx="0" cy="0" r="4.5" fill="#00F0FF" filter="url(#subtle-glow)"/>
      <circle cx="0" cy="0" r="9" fill="none" stroke="#00F0FF" stroke-width="0.8" opacity="0.5"/>
    </g>
    <!-- Outer Satellite 2: ORBIT AI -->
    <g transform="translate(175, 284)">
      <circle cx="0" cy="0" r="4" fill="#38BDF8" filter="url(#subtle-glow)"/>
      <circle cx="0" cy="0" r="8" fill="none" stroke="#38BDF8" stroke-width="0.8" opacity="0.5"/>
    </g>
  </g>

  <!-- Middle Orbiting Ring (CW) -->
  <g class="orbit-cw">
    <circle cx="175" cy="170" r="92" fill="none" stroke="#0070F3" stroke-width="1.8" stroke-dasharray="32 12 12 12" stroke-opacity="0.8"/>
    <!-- Middle Satellite 3: vLLM -->
    <g transform="translate(267, 170)">
      <circle cx="0" cy="0" r="3.5" fill="#C084FC" filter="url(#subtle-glow)"/>
      <circle cx="0" cy="0" r="7" fill="none" stroke="#C084FC" stroke-width="0.8" opacity="0.5"/>
    </g>
    <!-- Middle Satellite 4: PAIR -->
    <g transform="translate(83, 170)">
      <circle cx="0" cy="0" r="3.5" fill="#10B981" filter="url(#subtle-glow)"/>
      <circle cx="0" cy="0" r="7" fill="none" stroke="#10B981" stroke-width="0.8" opacity="0.5"/>
    </g>
  </g>

  <!-- Radar Scanning Beam -->
  <g class="radar-sweep">
    <path d="M 175 170 L 175 78 A 92 92 0 0 1 240 105 Z" fill="url(#radar-beam)"/>
    <line x1="175" y1="170" x2="175" y2="78" stroke="#00F0FF" stroke-width="1.8" opacity="0.9" filter="url(#subtle-glow)"/>
  </g>

  <!-- Inner Core Housing Base -->
  <circle cx="175" cy="170" r="72" fill="#01040A" stroke="#0070F3" stroke-width="1.8" stroke-opacity="0.7"/>
  <circle cx="175" cy="170" r="66" fill="#020308" stroke="#1E293B" stroke-width="1"/>

  <!-- Glowing Kairo Glass Logo Emblem -->
  <g class="core-reactor">
    <image href="data:image/png;base64,{logo_b64}" x="108" y="103" width="134" height="134" clip-path="url(#logo-circle-clip)"/>
    <!-- Glass Lens Overlay Ring -->
    <circle cx="175" cy="170" r="62" fill="none" stroke="#00F0FF" stroke-width="1.2" stroke-opacity="0.45"/>
  </g>

  <!-- Orbit Labels -->
  <text x="175" y="324" text-anchor="middle" class="hud-mono" font-size="9" fill="#64748B" font-weight="700" letter-spacing="1.5">KAIRO ORBIT // CORE ENGINE</text>

  <!-- ==================== RIGHT: MISSION CONTROL HUD ==================== -->

  <!-- Top Header Bar -->
  <g transform="translate(360, 36)">
    <!-- Live Green LED -->
    <circle cx="4" cy="-4" r="3.8" fill="#10B981" class="led-live"/>
    <circle cx="4" cy="-4" r="7" fill="none" stroke="#10B981" stroke-width="0.8" opacity="0.4"/>

    <!-- Title -->
    <text x="18" y="0" class="hud-title" font-size="12" fill="#F8FAFC">KAIRO CLOUD OS // TELEMETRY KERNEL</text>
    <text x="345" y="-1" class="hud-mono" font-size="10" fill="#38BDF8" font-weight="600">v2.6 PROD</text>

    <!-- Status Pill -->
    <rect x="390" y="-12" width="70" height="17" rx="8.5" fill="#0070F3" fill-opacity="0.15" stroke="#0070F3" stroke-width="1" stroke-opacity="0.4"/>
    <text x="425" y="0" text-anchor="middle" class="hud-mono" font-size="9" fill="#38BDF8" font-weight="700">ONLINE</text>
  </g>

  <!-- Header Divider with Laser Packet -->
  <line x1="360" y1="46" x2="820" y2="46" stroke="#1E293B" stroke-width="1"/>
  <line x1="360" y1="46" x2="440" y2="46" stroke="#00F0FF" stroke-width="1.5" stroke-opacity="0.8" filter="url(#subtle-glow)"/>

  <!-- Three Top Stat Metric Cards -->
  <!-- Card 1: Velocity / Commits -->
  <g transform="translate(360, 58)">
    <rect x="0" y="0" width="145" height="54" rx="8" fill="#060C1B" stroke="#1E293B" stroke-width="1"/>
    <text x="12" y="18" class="hud-label" font-size="9" fill="#64748B" font-weight="700">TOTAL ACTIVITY</text>
    <text x="12" y="42" class="hud-mono" font-size="20" fill="#38BDF8" font-weight="800">{data['total_contributions']}</text>
    <text x="60" y="40" class="hud-mono" font-size="9" fill="#0070F3" font-weight="700">COMMITS</text>
  </g>

  <!-- Card 2: Repositories -->
  <g transform="translate(517, 58)">
    <rect x="0" y="0" width="145" height="54" rx="8" fill="#060C1B" stroke="#1E293B" stroke-width="1"/>
    <text x="12" y="18" class="hud-label" font-size="9" fill="#64748B" font-weight="700">REPOSITORIES</text>
    <text x="12" y="42" class="hud-mono" font-size="20" fill="#F8FAFC" font-weight="800">{data['repo_count']}</text>
    <text x="46" y="40" class="hud-mono" font-size="9" fill="#64748B" font-weight="700">CLUSTERS</text>
  </g>

  <!-- Card 3: Uptime / Efficiency -->
  <g transform="translate(675, 58)">
    <rect x="0" y="0" width="145" height="54" rx="8" fill="#060C1B" stroke="#1E293B" stroke-width="1"/>
    <text x="12" y="18" class="hud-label" font-size="9" fill="#64748B" font-weight="700">RUNTIME UPTIME</text>
    <text x="12" y="42" class="hud-mono" font-size="20" fill="#10B981" font-weight="800">{data['uptime']}</text>
    <text x="100" y="40" class="hud-mono" font-size="9" fill="#10B981" font-weight="700">SLA</text>
  </g>

  <!-- Middle Section: Languages & Stack Breakdown -->
  <text x="360" y="134" class="hud-label" font-size="10" fill="#64748B" font-weight="700" letter-spacing="1.2">RUNTIME STACK TELEMETRY</text>
  <line x1="535" y1="130" x2="820" y2="130" stroke="#1E293B" stroke-width="0.8" stroke-dasharray="4 4"/>

  {langs_svg_str}

  <!-- Lower Section: Activity Sparkline Waveform -->
  <g transform="translate(0, 12)">
    <text x="360" y="248" class="hud-label" font-size="10" fill="#64748B" font-weight="700" letter-spacing="1.2">ACTIVITY MOMENTUM (LAST 28 DAYS)</text>
    <text x="820" y="248" text-anchor="end" class="hud-mono" font-size="9" fill="#38BDF8" font-weight="600">VELOCITY: OPTIMAL</text>

    <!-- Sparkline Area & Line -->
    <path d="{sparkline_area}" fill="url(#sparkline-grad)"/>
    <path d="{sparkline_path}" fill="none" stroke="#00F0FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" filter="url(#subtle-glow)"/>

    <!-- Grid Baseline -->
    <line x1="360" y1="285" x2="820" y2="285" stroke="#1E293B" stroke-width="1"/>
  </g>

  <!-- Bottom Telemetry Status Strip -->
  <line x1="360" y1="310" x2="820" y2="310" stroke="#1E293B" stroke-width="0.8"/>
  <g transform="translate(360, 324)">
    <text x="0" y="0" class="hud-mono" font-size="9" fill="#475569">NODE: <tspan fill="#94A3B8">thekairo.dev</tspan></text>
    <text x="135" y="0" class="hud-mono" font-size="9" fill="#475569">ARCH: <tspan fill="#94A3B8">BROWSER-PTY</tspan></text>
    <text x="270" y="0" class="hud-mono" font-size="9" fill="#475569">PING: <tspan fill="#10B981">12ms</tspan></text>
    <text x="460" y="0" text-anchor="end" class="hud-mono" font-size="9" fill="#38BDF8" font-weight="600">FOUNDER &amp; CEO</text>
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

    print(f"Successfully generated telemetry visualizer: {OUTPUT_SVG}")

if __name__ == "__main__":
    main()
