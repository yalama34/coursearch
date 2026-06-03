import logging
import os
import sys


LOGGING_LEVEL: str = os.getenv('LOGGING_LEVEL', 'INFO')

def _parse_level(name: str) -> int:
    """
    Parses the logging level from string to int
    :param name: name of the logging level (may be in any case)
    :return: int value of the logging level (if function couldn't parse your name, it will return ``int``
    value of level ``logging.INFO``
    """
    level = getattr(logging, name.upper(), None)
    if isinstance(level, int):
        return level
    return logging.INFO

def configure_logging() -> None:
    """
    Configure root logging
    :return: ``None``
    """
    level_name = os.getenv('LOGGING_LEVEL', 'INFO').strip().upper()
    level = _parse_level(level_name)

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler(stream=sys.stderr)
        handler.setFormatter(
            logging.Formatter(
                '[ML-SERVICE]%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
            )
        )
        root_logger.addHandler(handler)

    root_logger.setLevel(level)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

    logging.getLogger("pipelines").setLevel(level)
    logging.getLogger("engine").setLevel(level)
    logging.getLogger("scripts").setLevel(level)
