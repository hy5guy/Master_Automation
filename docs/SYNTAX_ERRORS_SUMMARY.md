# Specific Syntax Errors Found in M Code

## File: `2026_01_12____Overtime_Timeoff_v3.m`

### Error 1: Lines 214-222 - Broken `let...in` structure in `IsPriorFile`

**Current (WRONG):**
```m
PeriodLabels = if Table.RowCount(SampleRows) > 0 
               then List.Distinct(Table.Column(SampleRows, "PeriodLabel"))
               else {
}
in List.Contains(PeriodLabels, "11-25") and
    not List.Contains(PeriodLabels, "12-25") else
```

**Should be:**
```m
PeriodLabels = if Table.RowCount(SampleRows) > 0 
               then List.Distinct(Table.Column(SampleRows, "PeriodLabel"))
               else {},
result = if List.Contains(PeriodLabels, "11-25") and
            not List.Contains(PeriodLabels, "12-25")
         then true
         else false
in
    result
```

### Error 2: Line 280 - Missing space after `then`

**Current (WRONG):**
```m
prior = if has then[Prior]{0}[Total] else null,
```

**Should be:**
```m
prior = if has then [Prior]{0}[Total] else null,
```

### Error 3: Lines 281-282 - Wrong `in` placement and spacing in operator

**Current (WRONG):**
```m
newv = [NewTotal] in if apply and has and newv<> null and
       newv < > 0 then prior / newv else 1.0,
```

**Should be:**
```m
newv = [NewTotal],
result = if apply and has and newv <> null and newv <> 0 
         then prior / newv 
         else 1.0
in
    result,
```

### Error 4: Line 290 - Missing spaces around operators

**Current (WRONG):**
```m
each let isAccrual = [BaseMetric]<> null, ftable = [F],
```

**Should be:**
```m
each let isAccrual = [BaseMetric] <> null, ftable = [F],
```

### Error 5: Line 291 - Missing space around operator

**Current (WRONG):**
```m
scale = if ftable<> null and Table.RowCount(ftable) > 0 and
```

**Should be:**
```m
scale = if ftable <> null and Table.RowCount(ftable) > 0 and
```

### Error 6: Line 294 - Missing spaces after keywords

**Current (WRONG):**
```m
result = if isAccrual then[Hours] * scale else[Hours] in result,
```

**Should be:**
```m
result = if isAccrual then [Hours] * scale else [Hours]
in
    result,
```

### Error 7: Line 324 - Missing space and incorrect operator spacing

**Current (WRONG):**
```m
ExcludeCurrent = Table.SelectRows(Renamed, each[PeriodLabel] < > "12-25"),
```

**Should be:**
```m
ExcludeCurrent = Table.SelectRows(Renamed, each [PeriodLabel] <> "12-25"),
```

### Error 8: Lines 304-332 - Complex `PriorVisualLong` structure needs fixing

The entire `PriorVisualLong` section has nested `let...in` blocks that need proper structure. The outer `if...then...else` should wrap the entire logic properly.

**Current structure is broken** - needs complete refactoring to ensure:
- All `let` blocks have proper `in` keywords
- All variable definitions are within `let` blocks
- The final `in` returns the correct value
- Proper indentation and structure

## Additional Issues to Check

- Line 224: `each[IsPrior]` → `each [IsPrior]`
- Line 228: `PriorCont<> null` → `PriorCont <> null`
- Line 237-244: `PriorAccruals` - verify `let...in` structure
- Line 246-257: `PriorAccrualsNorm` - verify `let...in` structure
- Line 259: `each[BaseMetric]<> null` → `each [BaseMetric] <> null`
- Line 342: `each[Time_Category] < >` → `each [Time_Category] <>`
- Line 353: `each[PeriodLabel]` → `each [PeriodLabel]`
- Line 394: `if[J]<> null` → `if [J] <> null`, `then[J]` → `then [J]`
