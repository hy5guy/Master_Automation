Fix cells in an Excel workbook (.xlsx/.xlsm) using zip-level XML surgery.

**NEVER use openpyxl load+save on shared workbooks** -- it strips Data Validation, Conditional Formatting, Web Extensions, and other XML extensions that Excel needs.

## Input

The user will provide:
- Workbook path
- Cell fixes: which cells to change, and to what (value or formula)

## Process

### Step 1: Inspect the target cells

Read the sheet XML from within the xlsx zip to see the exact XML for each target cell. xlsx files are zip archives -- use `zipfile.ZipFile` to read.

Map sheet names to sheet files via:
- `xl/workbook.xml` (sheet name -> rId)
- `xl/_rels/workbook.xml.rels` (rId -> Target file)

Print the full `<c ...>...</c>` element for each target cell so you can build exact string replacements.

### Step 2: Build exact string replacements

For each cell, construct an exact `old_string -> new_string` replacement. Rules:

- **Formula to value**: `<c r="X1" s="70"><f>...</f><v>...</v></c>` -> `<c r="X1" s="70"><v>NEW_VALUE</v></c>`
- **Formula to formula**: Replace only the `<f>` content, preserve `<v>` cache or remove it
- **Shared formula removal**: If removing a shared formula master (`<f t="shared" ref="..." si="N">`), also fix or remove ALL cells that reference the same `si="N"` group
- **Self-closing formula tags**: Watch for `<f t="shared" ... si="N"/>` (self-closing) followed by `<v>...</v></c>` -- match the FULL cell including closing `</c>`

### Step 3: Clean calcChain.xml

**CRITICAL**: If any cell changes FROM a formula TO a plain value, remove that cell's entry from `xl/calcChain.xml`. Entries look like `<c r="K3" i="4"/>` or `<c r="K3" i="4" l="1"/>`. The `i` attribute is the sheetId (from workbook.xml), NOT the sheet file number.

If a cell changes from one formula to another formula, leave its calcChain entry.

### Step 4: Write the fixed zip

```python
import zipfile, tempfile, os, re

# Build fix_map: {filename: {old: new, ...}}
# Build calcchain_removals: [(cell_ref, sheet_id), ...]

tmp_out = tempfile.NamedTemporaryFile(suffix=target.suffix, delete=False, dir=str(target.parent))
tmp_out.close()

with zipfile.ZipFile(str(target), 'r') as src_zip:
    with zipfile.ZipFile(tmp_out.name, 'w', zipfile.ZIP_DEFLATED) as dst_zip:
        for item in src_zip.infolist():
            data = src_zip.read(item.filename)

            if item.filename in fix_map:
                xml = data.decode('utf-8')
                for old, new in fix_map[item.filename].items():
                    xml = xml.replace(old, new)
                data = xml.encode('utf-8')

            elif item.filename == 'xl/calcChain.xml':
                xml = data.decode('utf-8')
                for ref, sheet_id in calcchain_removals:
                    xml = re.sub(r'<c r="' + ref + r'" i="' + sheet_id + r'"[^/]*/>', '', xml)
                data = xml.encode('utf-8')

            # MUST pass ZipInfo object (item), not string name -- preserves compression metadata
            dst_zip.writestr(item, data)

os.replace(tmp_out.name, str(target))
```

### Step 5: Create a backup first

Always `shutil.copy2()` to an `archive/` subfolder with timestamp before modifying.

## Critical Rules

1. **NEVER parse target XML through ElementTree** -- it silently drops namespace declarations, `mc:Ignorable`, and extension elements
2. **NEVER use openpyxl save** on the target workbook -- read-only analysis is OK
3. **Use exact string replacement** on raw XML bytes -- this preserves 100% of original content
4. **Always clean calcChain.xml** when removing formulas
5. **Always preserve ZipInfo objects** when rewriting zip entries (pass `item` not `item.filename` to `writestr`)
6. **Always backup first** to `archive/` subfolder with datestamp
7. **File must be closed in Excel** before writing -- check for PermissionError

## Applies To

All shared Excel workbooks in the Compstat pipeline, especially those in `Shared Folder\Compstat\Contributions\`.
