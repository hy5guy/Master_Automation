# Hackensack PD - HTML Report Style Prompt
# Reusable template: paste this into any AI prompt when requesting a formatted HTML report.
# Style source: Response_Time_Correction_Report_Chief_Antista_2026_02_26.html

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

**Typography**
- Body: Georgia, serif, 13.5px, color #2c2c3e, line-height 1.75
- Headings (h2): bold, 14px, uppercase, letter-spacing 1px, color #1a2744,
  border-bottom 2px solid #c8a84b, padding-bottom 5px, margin 28px 0 14px
- Headings (h3): bold, 13px, color #1a2744, margin 18px 0 8px
- Meta bar / small labels: 11-11.5px, sans-serif, color #444
- Table headers: 11px, uppercase, letter-spacing 0.5px

---

### PAGE STRUCTURE

```html
<body style="font-family:'Georgia',serif;font-size:13.5px;color:#1a1a2e;
             background:#f5f5f0;padding:40px 20px;">
  <div class="page"> <!-- max-width:820px; margin:0 auto; white card with border and box-shadow -->

    <!-- 1. HEADER BAND -->
    <!-- Navy background (#1a2744), gold bottom border (4px solid #c8a84b), padding 28px 40px 22px -->
    <!-- Contains: department label (gold, 11px, spaced caps), h1 (white, 20px), subtitle (slate, 12px italic) -->

    <!-- 2. META BAR -->
    <!-- Background #eef0f5, border-bottom 1px #d0d4de, padding 10px 40px -->
    <!-- Flex row with ~40px gap. Items: Prepared by | Version | Review | Status -->

    <!-- 3. CONTENT AREA -->
    <!-- padding 32px 40px 40px -->
    <!-- Sections separated by h2 with gold underline -->

    <!-- 4. FOOTER BAND -->
    <!-- Background #eef0f5, border-top 2px solid #1a2744, padding 12px 40px, font-size 10.5px -->
    <!-- Contains methodology note + version + date + repository path -->

  </div>
</body>
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
```
- Use for: bottom-line summaries, peer review confirmations, important callouts
- `<p>` inside has margin:0 and font-size 13px

#### Data Tables
```css
/* Table */
width:100%; border-collapse:collapse; font-size:12.5px; margin:14px 0 20px;

/* th */
background:#1a2744; color:white; padding:9px 12px; text-align:left;
font-size:11px; text-transform:uppercase; letter-spacing:0.5px;

/* td */
padding:8px 12px; border-bottom:1px solid #e8e8ee; vertical-align:top;

/* Alternating rows */
tr:nth-child(even) td { background:#f7f8fb; }

/* Value states */
td.wrong { color:#b71c1c; font-weight:bold; }   /* old/incorrect value */
td.right { color:#2e7d32; font-weight:bold; }   /* corrected value */
td.center { text-align:center; }
```
- For corrected-value tables use a darker green header: `background:#2e4a2e`

#### Summary / KPI Boxes (3-column grid)
```css
/* Grid */
display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px; margin:16px 0 24px;

/* Each box */
border:1px solid #d0d4de; border-radius:4px; padding:14px;
text-align:center; background:#fafbfd;

/* Label (category name) */
font-size:10.5px; text-transform:uppercase; letter-spacing:1px; color:#666; margin-bottom:6px;

/* Old value (struck through) */
font-size:18px; font-weight:bold; color:#b71c1c; text-decoration:line-through; opacity:0.7;

/* Arrow */
color:#888; font-size:13px; margin:2px 0;  /* use ▼ character */

/* New value */
font-size:22px; font-weight:bold; color:#2e7d32;

/* Sub-label (month / record count) */
font-size:10px; color:#888; margin-top:4px;
```

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
```
- Usage: `<span class="finding critical">Finding 1 - Critical</span>` inline before h3 text

#### Signature Block
```css
margin-top:36px; padding-top:20px; border-top:1px solid #d0d4de;
display:grid; grid-template-columns:1fr 1fr; gap:40px; font-size:12px;

/* Signature line */
border-top:1px solid #333; padding-top:6px; margin-top:40px; color:#555;
```

#### Print Media Query (always include)
```css
@media print {
  body { background:white; padding:0; }
  .page { box-shadow:none; border:none; }
}
```

---

### FULL CSS BLOCK (copy-paste ready)

```css
* { box-sizing:border-box; margin:0; padding:0; }

body {
  font-family:'Georgia',serif; font-size:13.5px;
  color:#1a1a2e; background:#f5f5f0; padding:40px 20px;
}
.page {
  max-width:820px; margin:0 auto; background:#ffffff;
  border:1px solid #ccc; box-shadow:0 2px 12px rgba(0,0,0,0.12);
}
.header {
  background:#1a2744; color:white;
  padding:28px 40px 22px; border-bottom:4px solid #c8a84b;
}
.header .dept {
  font-size:11px; letter-spacing:2px; text-transform:uppercase;
  color:#c8a84b; margin-bottom:6px;
}
.header h1 { font-size:20px; font-weight:bold; line-height:1.3; margin-bottom:4px; }
.header .subtitle { font-size:12px; color:#b0b8cc; font-style:italic; }
.meta-bar {
  background:#eef0f5; border-bottom:1px solid #d0d4de;
  padding:10px 40px; display:flex; gap:40px;
  font-size:11.5px; color:#444;
}
.meta-bar span strong { color:#1a2744; }
.content { padding:32px 40px 40px; }
h2 {
  font-size:14px; font-weight:bold; color:#1a2744;
  text-transform:uppercase; letter-spacing:1px;
  border-bottom:2px solid #c8a84b; padding-bottom:5px;
  margin:28px 0 14px;
}
h2:first-of-type { margin-top:0; }
h3 { font-size:13px; font-weight:bold; color:#1a2744; margin:18px 0 8px; }
p { line-height:1.75; margin-bottom:12px; color:#2c2c3e; }
.alert {
  background:#fff8e6; border-left:4px solid #c8a84b;
  padding:14px 18px; margin:16px 0; border-radius:0 4px 4px 0;
}
.alert.green { background:#f0faf2; border-left-color:#2e7d32; }
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
  letter-spacing:1px; color:#666; margin-bottom:6px;
}
.summary-box .old-val {
  font-size:18px; font-weight:bold;
  color:#b71c1c; text-decoration:line-through; opacity:0.7;
}
.summary-box .arrow { color:#888; font-size:13px; margin:2px 0; }
.summary-box .new-val { font-size:22px; font-weight:bold; color:#2e7d32; }
.summary-box .type { font-size:10px; color:#888; margin-top:4px; }
table {
  width:100%; border-collapse:collapse;
  font-size:12.5px; margin:14px 0 20px;
}
th {
  background:#1a2744; color:white; padding:9px 12px;
  text-align:left; font-size:11px;
  text-transform:uppercase; letter-spacing:0.5px;
}
td {
  padding:8px 12px; border-bottom:1px solid #e8e8ee;
  vertical-align:top;
}
tr:nth-child(even) td { background:#f7f8fb; }
td.wrong { color:#b71c1c; font-weight:bold; }
td.right { color:#2e7d32; font-weight:bold; }
td.center { text-align:center; }
.val-table th { background:#2e4a2e; }
.finding {
  display:inline-block; font-size:10px; font-weight:bold;
  text-transform:uppercase; letter-spacing:0.5px;
  padding:2px 8px; border-radius:3px;
  margin-right:6px; vertical-align:middle;
}
.finding.critical { background:#ffebee; color:#b71c1c; border:1px solid #ef9a9a; }
.finding.high     { background:#fff8e6; color:#e65100; border:1px solid #ffcc80; }
.finding.info     { background:#e8f5e9; color:#2e7d32; border:1px solid #a5d6a7; }
.signature {
  margin-top:36px; padding-top:20px; border-top:1px solid #d0d4de;
  display:grid; grid-template-columns:1fr 1fr; gap:40px; font-size:12px;
}
.sig-line {
  border-top:1px solid #333; padding-top:6px;
  margin-top:40px; color:#555;
}
.footer {
  background:#eef0f5; border-top:2px solid #1a2744;
  padding:12px 40px; font-size:10.5px; color:#666; line-height:1.6;
}
@media print {
  body { background:white; padding:0; }
  .page { box-shadow:none; border:none; }
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
    <div class="dept">City of Hackensack - Police Department</div>
    <h1>[REPORT TITLE]</h1>
    <div class="subtitle">Internal Report &nbsp;|&nbsp; [DATE] &nbsp;|&nbsp; Prepared for [RECIPIENT]</div>
  </div>

  <div class="meta-bar">
    <span><strong>Prepared by:</strong> R. A. Carucci, Principal Analyst</span>
    <span><strong>Date:</strong> [DATE]</span>
    <span><strong>Subject:</strong> [SUBJECT]</span>
    <span><strong>Status:</strong> [STATUS]</span>
  </div>

  <div class="content">

    <h2>Executive Summary</h2>
    <p>[Summary paragraph]</p>
    <div class="alert">
      <p><strong>Bottom line:</strong> [Key takeaway sentence.]</p>
    </div>

    <h2>[Section Title]</h2>
    <h3><span class="finding critical">Finding 1 - Critical</span> [Finding Title]</h3>
    <p>[Body text]</p>

    <h3><span class="finding high">Finding 2 - High</span> [Finding Title]</h3>
    <p>[Body text]</p>

    <h3><span class="finding info">Finding 3 - Informational</span> [Finding Title]</h3>
    <p>[Body text]</p>

    <!-- KPI summary boxes -->
    <h2>[KPI Section Title]</h2>
    <div class="summary-grid">
      <div class="summary-box">
        <div class="label">[Metric Label]</div>
        <div class="old-val">[Old Value]</div>
        <div class="arrow">▼</div>
        <div class="new-val">[New Value]</div>
        <div class="type">[Month] &nbsp;|&nbsp; [N] records</div>
      </div>
      <!-- repeat summary-box as needed -->
    </div>

    <!-- Data table -->
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

    <!-- Green confirmation alert -->
    <div class="alert green">
      <p><strong>[Confirmation label]:</strong> [Confirmation text.]</p>
    </div>

    <!-- Signature block -->
    <div class="signature">
      <div>
        <div class="sig-line">
          R. A. Carucci, Principal Analyst<br>City of Hackensack Police Department
        </div>
      </div>
      <div>
        <div class="sig-line">
          [Recipient Name]<br>[Recipient Title]
        </div>
      </div>
    </div>

  </div><!-- /content -->

  <div class="footer">
    <strong>Note:</strong> [Methodology or disclaimer text.] &nbsp;|&nbsp;
    <strong>Version:</strong> [vX.X.X] &nbsp;|&nbsp;
    <strong>Date:</strong> [DATE] &nbsp;|&nbsp;
    <strong>Repository:</strong> Master_Automation / [path]
  </div>

</div><!-- /page -->
</body>
</html>
```

---

### QUICK REFERENCE - ELEMENT CHEAT SHEET

| Element | Class(es) | Purpose |
|---|---|---|
| Gold alert box | `.alert` | Bottom-line summary, key callout |
| Green alert box | `.alert.green` | Confirmed finding, success state |
| Critical badge | `.finding.critical` | Red badge before h3 |
| High badge | `.finding.high` | Orange badge before h3 |
| Info badge | `.finding.info` | Green badge before h3 |
| KPI grid | `.summary-grid` + `.summary-box` | 3-column before/after value boxes |
| Standard table | `table` + `th`/`td` | Navy header, alternating rows |
| Corrected-values table | `table.val-table` | Dark green header variant |
| Wrong value | `td.wrong` | Red bold strikethrough |
| Correct value | `td.right` | Green bold |
| Centered cell | `td.center` | Numeric data |
| Signature block | `.signature` | Two-column sign-off at bottom |

<!-- ============================================================
     END OF STYLE BLOCK
     ============================================================ -->
