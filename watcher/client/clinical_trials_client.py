import csv
import logging
import requests
from io import StringIO
from typing import Dict, Optional, Iterator

from watcher.config.settings import settings

logger = logging.getLogger("watcher.client")

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def stream_studies(
    cutoff_date: Optional[str] = None,
) -> Iterator[Dict]:
    """
    Stream studies from ClinicalTrials.gov using CSV format.

    - Sorted by LastUpdatePostDate DESC
    - Streams page-by-page (constant memory)
    - Stops pagination early once cutoff_date is crossed
    - Logs per-page and run-level date ranges
    """
    next_page_token = None
    page_num = 1

    max_seen_date: Optional[str] = None
    min_seen_date: Optional[str] = None

    logger.info("Starting CSV stream from ClinicalTrials.gov")
    logger.info("pageSize=%d", settings.PAGE_SIZE)
    logger.info("Sorting by LastUpdatePostDate DESC")

    if cutoff_date:
        logger.info("Applying cutoff_date=%s", cutoff_date)

    while True:
        params = {
            "format": "csv",
            "pageSize": settings.PAGE_SIZE,

            # IMPORTANT:
            # sort uses DATA STRUCTURE field name, NOT CSV column name
            "sort": "LastUpdatePostDate",

            # CSV column names (as per CSV Download docs)
            "fields": ",".join([
                "NCT Number",
                "Study Title",
                "Study Status",
                "Study Type",
                "Phases",
                "Enrollment",
                "Conditions",
                "Sponsor",
                "Funder Type",
                "Start Date",
                "Completion Date",
                "Last Update Posted",
                "Results First Posted",
            ]),
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        logger.info(
            "Fetching page %d (pageToken=%s)",
            page_num,
            next_page_token,
        )

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=60,
        )
        response.raise_for_status()

        logger.info(
            "HTTP 200 received (payload=%d bytes)",
            len(response.content),
        )

        next_page_token = response.headers.get("x-next-page-token")
        logger.info("Next page token: %s", next_page_token)

        reader = csv.DictReader(StringIO(response.text))
        page_row_count = 0

        for row in reader:
            page_row_count += 1

            record = _normalize_row(row)
            last_update = record.get("last_update_posted")

            # Track global min/max dates for observability
            if last_update:
                if max_seen_date is None or last_update > max_seen_date:
                    max_seen_date = last_update
                if min_seen_date is None or last_update < min_seen_date:
                    min_seen_date = last_update

            # EARLY TERMINATION (sorted DESC guarantees correctness)
            if cutoff_date and last_update and last_update < cutoff_date:
                logger.info(
                    "Cutoff reached: row_date=%s < cutoff=%s. Stopping pagination.",
                    last_update,
                    cutoff_date,
                )
                logger.info(
                    "Run date range observed: [%s → %s]",
                    min_seen_date,
                    max_seen_date,
                )
                return

            yield record

        logger.info(
            "Page %d parsed (%d rows). Date range so far: [%s → %s]",
            page_num,
            page_row_count,
            min_seen_date,
            max_seen_date,
        )

        if not next_page_token:
            logger.info("No next page token. Pagination complete.")
            break

        page_num += 1

    logger.info(
        "Streaming completed. Final date range: [%s → %s]",
        min_seen_date,
        max_seen_date,
    )


def _normalize_row(row: Dict) -> Dict:
    """
    Normalize a single CSV row into internal schema.
    """
    return {
        "nct_id": row.get("NCT Number", "").strip(),
        "brief_title": row.get("Study Title", "").strip(),
        "overall_status": row.get("Study Status", "").strip(),
        "study_type": row.get("Study Type", "").strip(),
        "phase": row.get("Phases", "").strip(),
        "enrollment": row.get("Enrollment", "").strip(),
        "condition": row.get("Conditions", "").strip(),
        "lead_sponsor": row.get("Sponsor", "").strip(),
        "start_date": row.get("Start Date", "").strip(),
        "completion_date": row.get("Completion Date", "").strip(),
        "last_update_posted": row.get("Last Update Posted", "").strip(),
        "results_first_posted_date": row.get("Results First Posted", "").strip(),
        "source_last_fetched_at": "",  # populated at write time if needed
    }
