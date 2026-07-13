# SYSTEM SPECIFICATION: Templates

This document contains reusable Markdown/HTML templates to ensure future additions to the profile remain consistent with the System Specification architecture.

## 1. Repository Card Template (Component View)

When adding a new minor project, use this minimalist HTML table structure instead of standard Markdown bullet points to maintain the structured, documentation-like layout.

```html
<table width="100%">
  <tr>
    <td width="30%"><strong>[PROJECT_NAME]</strong></td>
    <td>
      [One sentence explaining the technical achievement].<br>
      <sub><strong>Stack:</strong> [Tech 1], [Tech 2] | <strong>Role:</strong> [Your Role]</sub><br>
      <a href="[URL]">Repository</a>
    </td>
  </tr>
</table>
```

## 2. Project Banner Template (Major Deployment View)

For major applications (like Alpha and Beta), use this side-by-side flexbox alternative (using HTML table columns) to ensure responsive rendering across all GitHub clients.

```html
<table width="100%">
  <tr>
    <td valign="top" width="50%">
      <h3>[PROJECT TITLE]</h3>
      <sub>[High-Level Description]</sub><br><br>
      <strong>Problem:</strong> [What specific constraint was solved?]<br>
      <strong>Solution:</strong> [How did you solve it technically?]<br>
      <strong>Decisions:</strong> [One interesting architectural decision.]<br>
      <br>
      <a href="[URL]">Repository</a> • <a href="[URL]">Live Endpoint</a> • <a href="[URL]">Documentation</a>
    </td>
    <td valign="top" width="50%">
      <img src="./assets/svg/[project-diagram].svg" alt="[Project] Architecture Diagram" width="100%">
    </td>
  </tr>
</table>
```
