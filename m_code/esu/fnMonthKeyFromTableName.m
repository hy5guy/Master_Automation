// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/esu/fnMonthKeyFromTableName.m
// # Author: R. A. Carucci
// # Purpose: Parse ESU sheet name (_YY_MMM) to first day of month as date for MonthKey.

(name as text) as nullable date =>
let
    n0 = Text.Upper(name),
    n1 = if Text.StartsWith(n0, "_") then Text.Range(n0, 1) else n0,
    yy = Text.Start(n1, 2),
    rest0 = Text.Range(n1, 2),
    rest1 = Text.Replace(rest0, "_", ""),
    rest2 = if Text.StartsWith(rest1, "D") then Text.Range(rest1, 1) else rest1,
    token4 = Text.End(rest2, 4),
    token3 = Text.End(rest2, 3),
    monthToken = if List.Contains({"JUNE","JULY"}, token4) then token4 else token3,
    monthMap = [
        JAN=1, FEB=2, MAR=3, APR=4, MAY=5,
        JUN=6, JUNE=6,
        JUL=7, JULY=7,
        AUG=8, SEP=9, OCT=10, NOV=11, DEC=12
    ],
    monthNum = try Record.Field(monthMap, monthToken) otherwise null,
    yearNum = try Number.FromText(yy) otherwise null,
    result = if monthNum = null or yearNum = null then null else #date(yearNum, monthNum, 1)
in
    result
