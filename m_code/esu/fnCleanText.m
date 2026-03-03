// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/esu/fnCleanText.m
// # Author: R. A. Carucci
// # Purpose: Clean text from ESU workbook (trim, replace nbsp, trim) for Tracked Items and other fields.

(fnText as nullable text) as text =>
let
    t0 = if fnText = null then "" else fnText,
    t1 = Text.Replace(t0, Character.FromNumber(160), " "),
    t2 = Text.Clean(t1),
    t3 = Text.Trim(t2)
in
    t3
