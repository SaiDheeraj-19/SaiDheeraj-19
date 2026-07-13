# SYSTEM SPECIFICATION: Maintenance & Extensibility

A profile README is a living document. To ensure the R. Sai Dheeraj "System Specification" profile remains memorable over time without degrading into chaos, adhere to these rules when updating.

## 1. Updating the Profile

- **Always replace, never just add.** If you add a new major project to `5.0 PRODUCTION DEPLOYMENTS`, remove the oldest or least impressive one. Keep the maximum number of featured major deployments to two or three. The profile must feel curated.
- **Maintain the tone.** Do not slip into using first-person adjectives ("I am an amazing developer"). Continue using the objective, system-oriented voice ("The entity... operates... deploys...").
- **Do not introduce new formatting.** Stick exclusively to the HTML tables and Markdown structures defined in this system.

## 2. Future Extensibility

If you need to add entirely new sections in the future, adhere to the numbering schema:

- Need a section for publications or writing? 
  - Add `[7.5] TECHNICAL MANUSCRIPTS`.
- Need a section for conference talks? 
  - Add `[6.5] BROADCASTED TRANSMISSIONS`.

## 3. Dynamic GitHub Data Integration

The profile currently uses static and some dynamic generated SVG endpoints (like GitHub Readme Stats and the Snake animation).
- Ensure the GitHub Action that generates the snake animation is running reliably (e.g., set to run every 24 hours via cron).
- If GitHub introduces a breaking change to their Markdown renderer that breaks the HTML tables, refactor the tables into standard Markdown tables or CSS flex grids if GitHub ever supports inline CSS `<style>` blocks (they currently do not).

By treating this README as a strict, enterprise-level codebase, it will remain an unforgettable digital artifact for years to come.
