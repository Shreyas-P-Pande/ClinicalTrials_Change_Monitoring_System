"""
Canonical CSV schemas for ClinicalTrials.gov change monitoring.

Design principles:
- Flat, stable, monitoring-oriented
- Optimized for change detection and alerting
- NOT a mirror of the ClinicalTrials.gov API
"""

from typing import List

# ============================================================
# FILE NAMES (production-style naming)
# ============================================================

STUDIES_LAST_FILE = "studies_last.csv"
STUDIES_CURRENT_SNAPSHOT_FILE = "studies_current_snapshot.csv"
CHANGE_LOG_FILE = "change_log.csv"


# ============================================================
# STUDIES SNAPSHOT SCHEMA
# (Used by BOTH last & current snapshot files)
# ============================================================

STUDIES_COLUMNS: List[str] = [
    # --- Identity ---
    "nct_id",                       # protocolSection.identificationModule.nctId

    # --- Titles / Context ---
    "brief_title",                  # identificationModule.briefTitle

    # --- Core lifecycle signals ---
    "overall_status",               # statusModule.overallStatus
    "study_type",                   # designModule.studyType
    "phase",                        # designModule.phases[0]
    "enrollment",                   # designModule.enrollmentInfo.count

    # --- Scientific / business context ---
    "condition",                    # conditionsModule.conditions[0]
    "lead_sponsor",                 # sponsorCollaboratorsModule.leadSponsor.name

    # --- Timeline ---
    "start_date",                   # statusModule.startDateStruct.date
    "completion_date",              # statusModule.completionDateStruct.date

    # --- Update detection anchors ---
    "last_update_posted",            # statusModule.lastUpdatePostDateStruct.date
    "results_first_posted_date",     # resultsFirstPostDateStruct.date (optional signal)

    # --- Internal traceability ---
    "source_last_fetched_at",        # UTC timestamp generated locally
]

# Mandatory columns — record is invalid without these
STUDIES_MANDATORY_COLUMNS: List[str] = [
    "nct_id",
    "brief_title",
    "overall_status",
    "study_type",
    "last_update_posted",
    "source_last_fetched_at",
]


# ============================================================
# CHANGE LOG SCHEMA
# (Audit trail + downstream summarization)
# ============================================================

CHANGE_LOG_COLUMNS: List[str] = [
    "event_id",             # UUID generated locally
    "nct_id",
    "change_type",          # NEW_TRIAL | UPDATED_TRIAL
    "field_name",           # Column name (null for NEW_TRIAL)
    "old_value",
    "new_value",
    "detected_at",          # UTC timestamp
    "last_update_posted",   # From ClinicalTrials.gov
]

CHANGE_LOG_MANDATORY_COLUMNS: List[str] = [
    "event_id",
    "nct_id",
    "change_type",
    "detected_at",
    "last_update_posted",
]