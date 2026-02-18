from typing import Dict, List


def diff_records(
    last_record: Dict,
    current_record: Dict,
    fields_to_track: List[str],
) -> List[Dict]:
    """
    Compare two study records and return a list of field-level changes.

    Each change is represented as:
    {
        "field_name": str,
        "old_value": Any,
        "new_value": Any
    }
    """
    changes = []

    for field in fields_to_track:
        old_value = _normalize(last_record.get(field))
        new_value = _normalize(current_record.get(field))

        if old_value != new_value:
            changes.append({
                "field_name": field,
                "old_value": old_value,
                "new_value": new_value,
            })

    return changes


# ============================================================
# Helpers
# ============================================================

def _normalize(value):
    """
    Normalize values for reliable comparison.
    """
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    return value