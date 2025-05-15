from flask import jsonify

from src.logger_config import get_logger

logger = get_logger("api-profiles")

def get_error_json(title, detail, url, method="GET"):
    logger.error(f"Profile API - {method} {url} - {title}: {detail}")
    return jsonify(
        {
            "type": "about:blank",
            "title": title,
            "status": 0,
            "detail": f"{title}: {detail}",
            "instance": url,
        }
    )
