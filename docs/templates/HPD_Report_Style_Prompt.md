# Hackensack PD - HTML Report Style Prompt
# Reusable template: paste this into any AI prompt when requesting a formatted HTML report.
# Style source: Master_Report_Template_SSOCC
# Incorporates: Key Findings, dynamic KPI arrows, print optimizations, document status colors

---

## HOW TO USE

Paste the block below (everything between the START and END markers) into your AI prompt,
then add your report-specific instructions after it. Replace the bracketed placeholders
with your actual content.

---

<!-- ============================================================
     START OF STYLE BLOCK - paste everything below this line
     ============================================================ -->

Generate the report as a single self-contained HTML file using the following design system
exactly. Do not use any external stylesheets, fonts, or scripts. All CSS must be inline in
a `<style>` block in the `<head>`.

---

### DESIGN SYSTEM

**Color palette**
- Navy (primary):       #1a2744   — used for header background, section headings, table headers
- Gold (accent):        #c8a84b   — used for header border-bottom, h2 underline, alert left-border
- Dark green (success): #2e7d32   — used for positive/corrected values, green alert border
- Dark red (error):     #b71c1c   — used for wrong/old values, strikethrough text
- Page background:      #f5f5f0   — light warm off-white behind the page card
- Card background:      #ffffff
- Meta bar background:  #eef0f5
- Body text:            #2c2c3e
- Muted text:           #555 / #666 / #888
- Document status:      Draft (#e65100), In Review (#1565c0), Final (#2e7d32)

**Typography**
- Body: 'Segoe UI', Arial, sans-serif, 13.5px, color #2c2c3e, line-height 1.4
  (Alternative for formal reports: 'Georgia', serif)
- Headings (h2): bold, 15px, uppercase, letter-spacing 1px, color #1a2744,
  border-bottom 2px solid #c8a84b, padding-bottom 5px, margin 28px 0 14px
- Headings (h3): bold, 13px, color #1a2744, margin 18px 0 8px
- Meta bar / small labels: 11-11.5px, sans-serif, color #444
- Table headers: 11px, uppercase, letter-spacing 0.5px

---

### PAGE STRUCTURE

```html
<body style="font-family:'Segoe UI',Arial,sans-serif;font-size:13.5px;color:#1a1a2e;
             background:#f5f5f0;padding:40px 20px;">
  <div class="page"> <!-- max-width:900px; margin:0 auto; white card with border and box-shadow -->

    <!-- 1. HEADER BAND -->
    <!-- Navy background (#1a2744), gold bottom border (4px solid #c8a84b), padding 28px 24px 22px -->
    <!-- Stacked: dept (gold, 11px caps), h1 (white, 20px), subtitle (slate, 12px italic) -->

    <!-- 2. META BAR -->
    <!-- Background #eef0f5, border-bottom 1px #d0d4de, padding 14px 24px -->
    <!-- Flex row with ~40px gap. Items: Prepared by | Date | Subject | Status -->
    <!-- Status: use .status-draft (orange), .status-review (blue), or .status-final (green) -->

    <!-- 3. CONTENT AREA -->
    <!-- padding 32px 24px 40px -->
    <!-- Sections separated by h2 with gold underline -->

    <!-- 4. FOOTER BAND -->
    <!-- Background #eef0f5, border-top 2px solid #1a2744, padding 12px 24px, font-size 10.5px -->
    <!-- Contains methodology note + version + date + repository path -->

  </div>
</body>
```

---

### HEADER

```html
<div class="header">
  <div class="dept">City of Hackensack | Police Department | [Unit]</div>
  <h1>[REPORT TITLE]</h1>
  <div class="subtitle">Report Date: [DATE] &nbsp;&bull;&nbsp; Prepared for: [RECIPIENT]</div>
</div>
```

---

### COMPONENT SPECIFICATIONS

#### Alert / Callout Box
```css
/* Default (gold) */
background: #fff8e6; border-left: 4px solid #c8a84b;
padding: 14px 18px; margin: 16px 0; border-radius: 0 4px 4px 0;

/* Green variant (confirmed/success) */
background: #f0faf2; border-left: 4px solid #2e7d32;

/* Red variant (error/critical) */
background: #fff0f0; border-left: 4px solid #b71c1c;
```
- Use for: key findings summaries, peer review confirmations, important callouts
- **Label:** Use `<span class="alert-icon">&#9654;</span> <strong>Key Findings:</strong>` (icon in separate span to avoid PDF rendering issues)
- `<p>` inside has margin:0 and font-size 13px

#### Data Tables
```css
/* Table */
width:100%; border-collapse:collapse; font-size:12.5px; margin:14px 0 20px;

/* th */
background:#1a2744; color:white; padding:9px 12px; text-align:center;
font-size:11px; text-transform:uppercase; letter-spacing:0.5px;
th.th-nowrap { white-space:nowrap; }

/* td */
padding:8px 12px; border-bottom:1px solid #e8e8ee; vertical-align:top;

/* Alternating rows */
tr:nth-child(even) td { background:#f7f8fb; }

/* Value states */
td.wrong { color:#b71c1c; font-weight:bold; }   /* old/incorrect value */
td.right { color:#2e7d32; font-weight:bold; }   /* corrected value */
td.center { text-align:center; }
td.neutral { color:#555; font-style:italic; }   /* excluded/note cells */
```
- For corrected-value tables use a darker green header: `background:#2e4a2e`
- **Primary crimes / wide-first-column tables:** Add `class="primary-crimes"` — first column min-width 200px, numeric columns tight
- **Tables with notes column:** Add `class="table-notes"` — last column min-width 240px for notes/descriptions

#### Summary / KPI Boxes (3-column grid)
```css
/* Grid */
display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px; margin:16px 0 24px;

/* Each box */
border:1px solid #d0d4de; border-radius:4px; padding:14px;
text-align:center; background:#fafbfd;

/* Label (category name) */
font-size:10.5px; text-transform:uppercase; letter-spacing:1px; color:#444; margin-bottom:6px;

/* Value variants */
.summary-box .new-val { font-size:22px; font-weight:bold; color:#2e7d32; }
.summary-box .new-val.zero { color:#555; }   /* zero/neutral value */
.summary-box .new-val.warn { color:#e65100; } /* warning value */

/* Old value (struck through) - for before/after */
.summary-box .old-val { font-size:18px; font-weight:bold; color:#b71c1c; text-decoration:line-through; opacity:0.7; }

/* Arrow - supports both directions */
.summary-box .arrow { color:#888; font-size:13px; margin:2px 0; }
.summary-box .arrow-up { color:#2e7d32; font-size:13px; margin:2px 0; }   /* ▲ improvement */
.summary-box .arrow-down { color:#b71c1c; font-size:13px; margin:2px 0; } /* ▼ decline */

/* Sub-label */
.summary-box .type { font-size:10px; color:#666; margin-top:4px; }
```
- **Arrow logic:** Use `▲` (U+25B2) for improvement/increase, `▼` (U+25BC) for decline/decrease. Omit the arrow div entirely if no directional change. Apply `.arrow`, `.arrow-up`, or `.arrow-down` as appropriate.

#### Finding / Severity Badges
```css
/* Base */
display:inline-block; font-size:10px; font-weight:bold; text-transform:uppercase;
letter-spacing:0.5px; padding:2px 8px; border-radius:3px;
margin-right:6px; vertical-align:middle;

/* Critical */
background:#ffebee; color:#b71c1c; border:1px solid #ef9a9a;

/* High */
background:#fff8e6; color:#e65100; border:1px solid #ffcc80;

/* Info / Informational */
background:#e8f5e9; color:#2e7d32; border:1px solid #a5d6a7;

/* Neutral */
background:#f3f3f3; color:#555; border:1px solid #ccc;
```
- Usage: `<span class="finding critical">Finding 1 - Critical</span>` inline before h3 text

#### Excluded / Note Text
```css
.excluded-note { font-size:11px; color:#777; font-style:italic; }
```

#### Signature Block
```css
margin-top:36px; padding-top:20px; border-top:1px solid #d0d4de;
display:grid; grid-template-columns:1fr 1fr; gap:40px; font-size:13px;

/* Signature line */
.sig-line { border-top:1px solid #333; padding-top:6px; margin-top:40px; color:#333; font-weight:600; }
```
- Include optional Date line with extra spacing: `<br><span style="margin-top:16px; display:inline-block;">Date: _________________________</span>`

#### Print Media Query (always include)
```css
@media print {
  body { background:white; padding:0; }
  .page { box-shadow:none; border:none; max-width:100%; }
  @page { size: A4 portrait; margin: 20mm 18mm; }
}
```

---

### FULL CSS BLOCK (copy-paste ready)

```css
* { box-sizing:border-box; margin:0; padding:0; }

body {
  font-family:'Segoe UI', Arial, sans-serif; font-size:13.5px;
  color:#1a1a2e; background:#f5f5f0; padding:40px 20px;
}
.page {
  max-width:900px; margin:0 auto; background:#ffffff;
  border:1px solid #ccc; box-shadow:0 2px 12px rgba(0,0,0,0.12);
}
.header {
  background:#1a2744; color:white;
  padding:28px 24px 22px; border-bottom:4px solid #c8a84b;
}
.header .dept {
  font-size:11px; letter-spacing:2px; text-transform:uppercase;
  color:#c8a84b; margin-bottom:6px;
}
.header h1 { font-size:20px; font-weight:bold; line-height:1.3; margin-bottom:4px; }
.header .subtitle { font-size:12px; color:#b0b8cc; font-style:italic; }
.meta-bar {
  background:#eef0f5; border-bottom:1px solid #d0d4de;
  padding:14px 24px; display:flex; gap:40px;
  font-size:11.5px; color:#444; flex-wrap:wrap;
}
.meta-bar span strong { color:#1a2744; }
.status-draft { color:#e65100; font-weight:bold; }
.status-review { color:#1565c0; font-weight:bold; }
.status-final { color:#2e7d32; font-weight:bold; }
.content { padding:32px 24px 40px; }
h2 {
  font-size:15px; font-weight:bold; color:#1a2744;
  text-transform:uppercase; letter-spacing:1px;
  border-bottom:2px solid #c8a84b; padding-bottom:5px;
  margin:28px 0 14px;
}
h2:first-of-type { margin-top:0; }
h3 { font-size:13px; font-weight:bold; color:#1a2744; margin:18px 0 8px; }
p { line-height:1.4; margin-bottom:12px; color:#2c2c3e; }
.alert {
  background:#fff8e6; border-left:4px solid #c8a84b;
  padding:14px 18px; margin:16px 0; border-radius:0 4px 4px 0;
}
.alert-icon { margin-right:4px; }
.alert.green { background:#f0faf2; border-left-color:#2e7d32; }
.alert.red { background:#fff0f0; border-left-color:#b71c1c; }
.alert p { margin:0; font-size:13px; }
.alert strong { color:#1a2744; }
.summary-grid {
  display:grid; grid-template-columns:1fr 1fr 1fr;
  gap:14px; margin:16px 0 24px;
}
.summary-box {
  border:1px solid #d0d4de; border-radius:4px;
  padding:14px; text-align:center; background:#fafbfd;
}
.summary-box .label {
  font-size:10.5px; text-transform:uppercase;
  letter-spacing:1px; color:#444; margin-bottom:6px;
}
.summary-box .old-val {
  font-size:18px; font-weight:bold;
  color:#b71c1c; text-decoration:line-through; opacity:0.7;
}
.summary-box .arrow { color:#888; font-size:13px; margin:2px 0; }
.summary-box .arrow-up { color:#2e7d32; font-size:13px; margin:2px 0; }
.summary-box .arrow-down { color:#b71c1c; font-size:13px; margin:2px 0; }
.summary-box .new-val { font-size:22px; font-weight:bold; color:#2e7d32; }
.summary-box .new-val.zero { color:#555; }
.summary-box .new-val.warn { color:#e65100; }
.summary-box .type { font-size:10px; color:#666; margin-top:4px; }
table {
  width:100%; border-collapse:collapse;
  font-size:12.5px; margin:14px 0 20px;
}
th {
  background:#1a2744; color:white; padding:9px 12px;
  text-align:center; font-size:11px;
  text-transform:uppercase; letter-spacing:0.5px;
}
th.th-nowrap { white-space:nowrap; }
td {
  padding:8px 12px; border-bottom:1px solid #e8e8ee;
  vertical-align:top;
}
tr:nth-child(even) td { background:#f7f8fb; }
td.wrong { color:#b71c1c; font-weight:bold; }
td.right { color:#2e7d32; font-weight:bold; }
td.center { text-align:center; }
td.neutral { color:#555; font-style:italic; }
.table-notes td:last-child, .table-notes th:last-child { min-width: 240px; }
table.primary-crimes th:nth-child(1), table.primary-crimes td:nth-child(1) { min-width: 200px; }
table.primary-crimes th:nth-child(5), table.primary-crimes td:nth-child(5),
table.primary-crimes th:nth-child(6), table.primary-crimes td:nth-child(6) { min-width: 1em; width: 1%; }
table.primary-crimes td:last-child, table.primary-crimes th:last-child { min-width: auto; }
.val-table th { background:#2e4a2e; }
.finding {
  display:inline-block; font-size:10px; font-weight:bold;
  text-transform:uppercase; letter-spacing:0.5px;
  padding:2px 8px; border-radius:3px;
  margin-right:6px; vertical-align:middle;
}
.finding.critical { background:#ffebee; color:#b71c1c; border:1px solid #ef9a9a; }
.finding.high { background:#fff8e6; color:#e65100; border:1px solid #ffcc80; }
.finding.info { background:#e8f5e9; color:#2e7d32; border:1px solid #a5d6a7; }
.finding.neutral { background:#f3f3f3; color:#555; border:1px solid #ccc; }
.excluded-note { font-size:11px; color:#777; font-style:italic; }
.signature {
  margin-top:36px; padding-top:20px; border-top:1px solid #d0d4de;
  display:grid; grid-template-columns:1fr 1fr; gap:40px; font-size:13px;
}
.sig-line {
  border-top:1px solid #333; padding-top:6px;
  margin-top:40px; color:#333; font-weight:600;
}
.footer {
  background:#eef0f5; border-top:2px solid #1a2744;
  padding:12px 24px; font-size:10.5px; color:#666; line-height:1.6;
}
h2, h3 { page-break-after: avoid; }
table { page-break-inside: avoid; }
tr { page-break-inside: avoid; page-break-after: auto; }
thead { display: table-header-group; }
.alert, .summary-grid, .summary-box, .signature, .footer { page-break-inside: avoid; }
.header, .meta-bar { page-break-inside: avoid; }
.footer { page-break-before: avoid; }
@media print {
  body { background:white; padding:0; }
  .page { box-shadow:none; border:none; max-width:100%; }
  @page { size: A4 portrait; margin: 20mm 18mm; }
  .footer { font-size:9px; padding:8px 24px; line-height:1.3; }
}
```

---

### HTML SKELETON (copy-paste ready)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[REPORT TITLE]</title>
<style>
  /* --- paste full CSS block above here --- */
</style>
</head>
<body>
<div class="page">

  <div class="header">
    <div class="dept">City of Hackensack | Police Department | [UNIT]</div>
    <h1>[REPORT TITLE]</h1>
    <div class="subtitle">Report Date: [DATE] &nbsp;&bull;&nbsp; Prepared for: [RECIPIENT]</div>
  </div>

  <div class="meta-bar">
    <span><strong>Prepared by:</strong> R. A. Carucci #261, Principal Analyst</span>
    <span><strong>Date:</strong> [DATE]</span>
    <span><strong>Subject:</strong> [SUBJECT]</span>
    <span><strong>Status:</strong> <span class="status-final">[STATUS]</span></span> <!-- Use .status-draft, .status-review, or .status-final -->
  </div>

  <div class="content">

    <h2>Executive Summary</h2>
    <p>[Summary paragraph]</p>
    <div class="alert">
      <p><span class="alert-icon">&#9654;</span> <strong>Key Findings:</strong> [Key takeaway sentence.]</p>
    </div>

    <h2>[Section Title]</h2>
    <h3><span class="finding critical">Finding 1 - Critical</span> [Finding Title]</h3>
    <p>[Body text]</p>

    <h3><span class="finding high">Finding 2 - High</span> [Finding Title]</h3>
    <p>[Body text]</p>

    <h3><span class="finding info">Finding 3 - Informational</span> [Finding Title]</h3>
    <p>[Body text]</p>

    <!-- KPI summary boxes: Choose arrow based on metric direction. Use .arrow-up with ▲ for improvement/increase, .arrow-down with ▼ for decline/decrease, or omit the arrow div if no directional change. -->
    <h2>[KPI Section Title]</h2>
    <div class="summary-grid">
      <div class="summary-box">
        <div class="label">[Metric Label]</div>
        <div class="old-val">[Old Value]</div>
        <div class="arrow-up">▲</div>
        <div class="new-val">[New Value]</div>
        <div class="type">[Month] &nbsp;|&nbsp; [N] records</div>
      </div>
      <!-- repeat summary-box as needed; vary arrow class and character per metric -->
    </div>

    <!-- Data table: add class="primary-crimes" for wide first column; add class="table-notes" for wide last column (notes) -->
    <h2>[Table Section Title]</h2>
    <table>
      <thead>
        <tr>
          <th>[Col 1]</th><th>[Col 2]</th><th>[Col 3]</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>[value]</td>
          <td class="wrong">[old value]</td>
          <td class="right">[correct value]</td>
        </tr>
      </tbody>
    </table>

    <div class="alert green">
      <p><strong>[Confirmation label]:</strong> [Confirmation text.]</p>
    </div>

    <div class="signature">
      <div>
        <div class="sig-line">
          R. A. Carucci #261<br>
          Principal Analyst | Safe Streets Operations Control Center<br>
          Hackensack Police Department<br>
          <br>
          <span style="margin-top:16px; display:inline-block;">Date: _________________________</span>
        </div>
      </div>
    </div>

  </div><!-- /content -->

  <div class="footer">
    <strong>Note:</strong> [Methodology or disclaimer text.] &nbsp;|&nbsp;
    <strong>Version:</strong> [vX.X Final] &nbsp;|&nbsp;
    <strong>Date:</strong> [DATE] &nbsp;|&nbsp;
    <strong>Repository:</strong> 06_Workspace_Management / [path]
  </div>

</div><!-- /page -->
</body>
</html>
```

---

### QUICK REFERENCE - ELEMENT CHEAT SHEET

| Element | Class(es) | Purpose |
|---------|-----------|---------|
| Status (Draft) | `.status-draft` | Orange status in meta bar |
| Status (In Review) | `.status-review` | Blue status in meta bar |
| Status (Final) | `.status-final` | Green status in meta bar |
| Gold alert box | `.alert` | Key findings summary, key callout |
| Green alert box | `.alert.green` | Confirmed finding, success state |
| Red alert box | `.alert.red` | Error/critical callout |
| Critical badge | `.finding.critical` | Red badge before h3 |
| High badge | `.finding.high` | Orange badge before h3 |
| Info badge | `.finding.info` | Green badge before h3 |
| Neutral badge | `.finding.neutral` | Gray badge before h3 |
| KPI grid | `.summary-grid` + `.summary-box` | 3-column value boxes |
| KPI arrow (neutral) | `.arrow` | Gray arrow (▲ or ▼) |
| KPI arrow (up) | `.arrow-up` | Green ▲ for improvement |
| KPI arrow (down) | `.arrow-down` | Red ▼ for decline |
| Standard table | `table` + `th`/`td` | Navy header, alternating rows |
| Primary crimes table | `table.primary-crimes` | Wide first column, tight numeric columns |
| Table with notes column | `table.table-notes` | Wide last column for notes/descriptions |
| Corrected-values table | `table.val-table` | Dark green header variant |
| Wrong value | `td.wrong` | Red bold |
| Correct value | `td.right` | Green bold |
| Centered cell | `td.center` | Numeric data |
| Neutral/note cell | `td.neutral` | Gray italic |
| Excluded note | `.excluded-note` | Small italic paragraph |
| Signature block | `.signature` | Sign-off at bottom |

---

### CLERY ACT REPORT - GEOGRAPHY & METHODOLOGY NOTES

Use this block in the Geography & Methodology section of Clery reports. It documents filtering, buffering, and exclusions.

```html
<h2>Geography & Methodology</h2>
<p>
  Incidents were filtered from the full RMS export by campus location (FullAddress only; Narrative was not used to avoid false positives from detective follow-up references). Clery-reportable incident types were applied using NIBRS codes and descriptive terms.
</p>
<p>
  Public property geography is defined as a 100-foot buffer around campus locations. When a campus boundary feature class exists in the project geodatabase, the buffer was created from that polygon; otherwise, it was created from geocoded campus addresses. Incident points were geocoded via the NJ Geocoder service and projected to NJ State Plane for mapping.
</p>
<p>
  <strong>Excluded from this report:</strong> Incidents whose address did not match campus location terms; incidents that did not meet Clery-reportable categories when the incident-type filter was applied.
</p>
```

---

### CONVENTIONS

- **Key Findings** (not "Bottom Line") for executive summary callouts
- **Clery reports:** Include the "Geography & Methodology" block above to document filtering, buffering, and exclusions.
- **Non-Campus** (hyphenated) for Clery geography
- **CY-2025** (hyphenated) for calendar year
- **DOE Handbook 2020 ed.** for methodology references
- **Author/signature:** R. A. Carucci #261 | Principal Analyst | Safe Streets Operations Control Center | Hackensack Police Department

<!-- ============================================================
     END OF STYLE BLOCK
     ============================================================ -->
