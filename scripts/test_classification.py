"""Test classification logic."""

def classify_overtime_category(pay_type: str):
    """Classify overtime transaction as OT or COMP and extract rate."""
    pay_type = str(pay_type).lower()

    # COMP detection
    if any(term in pay_type for term in ['comp', 'compensatory', 'ct']):
        # Extract rate if present
        if '2.5' in pay_type or '250%' in pay_type:
            return 'COMP', '25'
        elif '2.0' in pay_type or '200%' in pay_type or 'double' in pay_type:
            return 'COMP', '20'
        elif '1.5' in pay_type or '150%' in pay_type:
            return 'COMP', '15'
        elif '1.0' in pay_type or '100%' in pay_type:
            return 'COMP', '10'
        return 'COMP', ''

    # OT detection (including cash with rate >= 1.5)
    ot_terms = ['overtime', 'o.t.', 'o/t', 'dt', 'double time', 'doubletime']
    if any(term in pay_type for term in ot_terms):
        # Extract rate
        if '2.5' in pay_type or '250%' in pay_type:
            return 'OT', '25'
        elif '2.0' in pay_type or '200%' in pay_type or 'double' in pay_type or 'dt' in pay_type:
            return 'OT', '20'
        elif '1.5' in pay_type or '150%' in pay_type:
            return 'OT', '15'
        return 'OT', '15'  # Default OT rate

    # Cash with rate >= 1.5
    if 'cash' in pay_type:
        if any(rate in pay_type for rate in ['1.5', '2.0', '2.5', '150%', '200%', '250%']):
            if '2.5' in pay_type or '250%' in pay_type:
                return 'OT', '25'
            elif '2.0' in pay_type or '200%' in pay_type:
                return 'OT', '20'
            elif '1.5' in pay_type or '150%' in pay_type:
                return 'OT', '15'

    return '', ''

# Test with actual values
test_cases = [
    "1.5 Comp Time",
    "1.5 Cash",
    "1.0 Comp Time",
    "1.0 Cash"
]

print("Testing classification:")
for tc in test_cases:
    cat, rate = classify_overtime_category(tc)
    print(f"  '{tc}' -> Category: {cat or 'NONE':5s}, Rate: {rate or 'NONE'}")
