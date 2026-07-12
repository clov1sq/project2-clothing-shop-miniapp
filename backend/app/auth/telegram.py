import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from app.core.errors import AppError


def validate_init_data(init_data: str, bot_token: str, max_age_seconds: int) -> dict[str, object]:
    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise AppError("TELEGRAM_AUTH_INVALID", "Некоректні дані Telegram", 401)

    data_check_string = "\n".join(f"{key}={pairs[key]}" for key in sorted(pairs))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calculated_hash, received_hash):
        raise AppError("TELEGRAM_AUTH_INVALID", "Не вдалося підтвердити Telegram", 401)

    try:
        auth_date = int(pairs.get("auth_date", "0"))
    except ValueError as exc:
        raise AppError("TELEGRAM_AUTH_INVALID", "Некоректна дата авторизації", 401) from exc
    if auth_date <= 0 or abs(int(time.time()) - auth_date) > max_age_seconds:
        raise AppError("TELEGRAM_AUTH_EXPIRED", "Сесію Telegram потрібно оновити", 401)

    raw_user = pairs.get("user")
    if not raw_user:
        raise AppError("TELEGRAM_USER_MISSING", "Telegram не передав користувача", 401)
    try:
        user = json.loads(raw_user)
    except json.JSONDecodeError as exc:
        raise AppError("TELEGRAM_AUTH_INVALID", "Некоректні дані користувача", 401) from exc
    if not isinstance(user, dict) or "id" not in user:
        raise AppError("TELEGRAM_USER_MISSING", "Telegram не передав користувача", 401)
    return user
