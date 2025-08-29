# utils/logging.py
import logging
import sys

def setup_logger():
    """
    Configure root logger for the project.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
