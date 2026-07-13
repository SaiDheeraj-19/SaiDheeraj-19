# SYSTEM SPECIFICATION: Design System

This document outlines the visual primitives and branding guidelines used to construct the R. Sai Dheeraj GitHub profile.

## 1. Typography Guide

To maintain a professional, minimal, and Apple/Linear-inspired aesthetic, the typography relies strictly on system fonts or universally readable fallbacks. 

- **Primary Font Stack**: `ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`
- **Monospace Font Stack** (for tags, code, and system nomenclature): `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace`
- **Heading Hierarchy**: 
  - `h1`: Reserved for major repository titles (not used in profile to maintain flatness).
  - `h2`: Used exclusively for `[MAJOR.MINOR] SYSTEM_SECTION` titles, rendered in monospace backticks to simulate code environments.
  - `h3`: Used for Component/Project titles.

## 2. Color Palette

The profile uses a hyper-minimalist palette designed to automatically adapt to GitHub's light/dark modes seamlessly, while feeling like an internal developer tool.

- **Backgrounds**: Transparent (`#00000000`) - relies entirely on the user's GitHub theme.
- **Primary Text**: Relies on GitHub's default Markdown body text color to ensure accessibility and theme conformity.
- **Secondary Text (Subtitles/Metadata)**: Managed via HTML `<sub>` tags for elegant contrast.
- **Accent Line/Borders**: Natural GitHub Markdown table borders (`<table width="100%">`) which automatically shift between light and dark mode.

## 3. Icon System

Instead of relying on heavy image assets or messy emojis, the icon system is governed by:
- **Feather Icons (SVG)**: Clean, stroke-based 24x24 icons where absolutely necessary (e.g., the closing clock icon).
- **Mermaid Graph Nodes**: Using standard rectangles and subtle curves.

*Note: Emojis are strictly banned from this design to maintain the enterprise-grade documentation aesthetic.*
