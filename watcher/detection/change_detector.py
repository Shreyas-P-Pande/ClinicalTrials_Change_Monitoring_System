import uuid
from datetime import datetime, timezone
from typing import Dict, List

from watcher.detection.diff_engine import diff_records


# ============================================================
# Configuration
# ============================================================

FIELDS_TO_TRACK = [
    "overall_status",
    "phase",
    "enrollment",
    "completion_date",
    "lead_sponsor",
]


# ============================================================
# Public API
# ============================================================

def detect_changes(
    last_records: Dict[str, Dict],
    current_records: Dict[str, Dict],
) -> List[Dict]:
    """
    Detect NEW_TRIAL and UPDATED_TRIAL events.

    Returns a list of change log records ready to be written
    to change_log.csv or sent to FastAPI.
    """
    events: List[Dict] = []

    for nct_id, current in current_records.items():
        last = last_records.get(nct_id)

        # ----------------------------------------------------
        # Case 1: New trial
        # ----------------------------------------------------
        if last is None:
            events.append(
                _new_trial_event(current)
            )
            continue

        # ----------------------------------------------------
        # Case 2: Potential update (date-based pre-filter)
        # ----------------------------------------------------
        if not _is_potential_update(last, current):
            continue

        # ----------------------------------------------------
        # Case 3: Confirmed update (field-level diff)
        # ----------------------------------------------------
        diffs = diff_records(
            last_record=last,
            current_record=current,
            fields_to_track=FIELDS_TO_TRACK,
        )

        for diff in diffs:
            events.append(
                _updated_trial_event(
                    current=current,
                    diff=diff,
                )
            )

    return events


# ============================================================
# Event builders
# ============================================================

def _new_trial_event(current: Dict) -> Dict:
    return {
        "event_id": _uuid(),
        "nct_id": current["nct_id"],
        "change_type": "NEW_TRIAL",
        "field_name": "",
        "old_value": "",
        "new_value": "",
        "detected_at": _utc_now(),
        "last_update_posted": current.get("last_update_posted", ""),
    }


def _updated_trial_event(current: Dict, diff: Dict) -> Dict:
    return {
        "event_id": _uuid(),
        "nct_id": current["nct_id"],
        "change_type": "UPDATED_TRIAL",
        "field_name": diff["field_name"],
        "old_value": diff["old_value"],
        "new_value": diff["new_value"],
        "detected_at": _utc_now(),
        "last_update_posted": current.get("last_update_posted", ""),
    }


# ============================================================
# Helpers
# ============================================================

def _is_potential_update(last: Dict, current: Dict) -> bool:
    """
    Date-based pre-filter.
    If last_update_posted did not advance, nothing material changed.
    """
    return (
        current.get("last_update_posted", "")
        > last.get("last_update_posted", "")
    )


def _uuid() -> str:
    return str(uuid.uuid4())


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()