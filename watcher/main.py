import time
import logging
import os
import shutil
from datetime import datetime, timedelta

from watcher.client.clinical_trials_client import stream_studies
from watcher.storage.csv_store import append_studies
from watcher.storage.schemas import (
    STUDIES_LAST_FILE,
    STUDIES_CURRENT_SNAPSHOT_FILE,
)
from watcher.storage.state_store import (
    load_last_known_update_date,
    save_last_known_update_date,
)
from watcher.config.settings import settings


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("watcher")


# ============================================================
# Helpers
# ============================================================

def compute_bootstrap_cutoff() -> str:
    """
    Compute bootstrap cutoff date (UTC) based on BOOTSTRAP_DAYS.
    """
    cutoff = datetime.utcnow() - timedelta(days=settings.BOOTSTRAP_DAYS)
    return cutoff.strftime("%Y-%m-%d")


# ============================================================
# Core watcher logic
# ============================================================

def run_once():
    logger.info("Starting watcher cycle")

    # --------------------------------------------------------
    # Load pipeline state
    # --------------------------------------------------------
    last_known_update_date = load_last_known_update_date()

    if not last_known_update_date:
        cutoff_date = compute_bootstrap_cutoff()
        logger.info(
            "BOOTSTRAP MODE: limiting fetch to last %d days (cutoff=%s)",
            settings.BOOTSTRAP_DAYS,
            cutoff_date,
        )
    else:
        cutoff_date = last_known_update_date
        logger.info(
            "INCREMENTAL MODE: cutoff=%s",
            cutoff_date,
        )

    # --------------------------------------------------------
    # Prepare current snapshot (clean per run)
    # --------------------------------------------------------
    current_snapshot_path = os.path.join("data", STUDIES_CURRENT_SNAPSHOT_FILE)

    if os.path.exists(current_snapshot_path):
        os.remove(current_snapshot_path)
        logger.info("Cleared previous current snapshot")

    # --------------------------------------------------------
    # Stream → append → discard (flat memory)
    # --------------------------------------------------------
    stream = stream_studies(cutoff_date=cutoff_date)

    written, max_update_date = append_studies(
        STUDIES_CURRENT_SNAPSHOT_FILE,
        stream,
    )

    logger.info(
        "Run completed. Records written=%d. Bootstrap window=%d days.",
        written,
        settings.BOOTSTRAP_DAYS,
    )

    logger.info("Total records written this run: %d", written)

    # --------------------------------------------------------
    # Update pipeline cursor (DATA-derived, not clock-based)
    # --------------------------------------------------------
    if max_update_date:
        save_last_known_update_date(max_update_date)
        logger.info(
            "Pipeline state updated (last_known_update_date=%s)",
            max_update_date,
        )
    else:
        logger.info("No new updates detected; pipeline state unchanged")

    # --------------------------------------------------------
    # Promote snapshot → last (atomic)
    # --------------------------------------------------------
    last_path = os.path.join("data", STUDIES_LAST_FILE)
    tmp_last_path = last_path + ".tmp"

    shutil.copyfile(current_snapshot_path, tmp_last_path)
    os.replace(tmp_last_path, last_path)

    logger.info("Promoted current snapshot to studies_last.csv")
    logger.info("Watcher cycle completed successfully")


# ============================================================
# Main loop
# ============================================================

def main():
    logger.info(
        "Watcher started. Polling every %d seconds",
        settings.POLL_INTERVAL_SECONDS,
    )

    while True:
        try:
            run_once()
        except Exception:
            logger.exception("Watcher cycle failed")

        time.sleep(settings.POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
