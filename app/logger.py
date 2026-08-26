import logging
from pathlib import Path

LOG_DIRECTORY = Path("logs")
LOG_DIRECTORY.mkdir(exist_ok=True)

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