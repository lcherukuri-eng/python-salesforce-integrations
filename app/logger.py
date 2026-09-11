import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DIRECTORY = BASE_DIR / "logs"

LOG_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
    handlers=[
        logging.FileHandler(
            LOG_DIRECTORY / "app.log"
        ),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    return logging.getLogger(name)