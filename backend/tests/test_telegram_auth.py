import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest

from app.auth.telegram import validate_init_data
from app.core.errors import AppError


def build_init_data(token: str, *, age: int = 0) -> str:
    values = {
        "auth_date": str(int(time.time()) - age),
        "query_id": "AAH_demo",
        "user": json.dumps({"id": 55, "first_name": "Test"}, separators=(",", ":")),
    }
    check = "\n".join(f"{key}={values[key]}" for key in sorted(values))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    values["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(values)


def test_valid_init_data() -> None:
    payload = validate_init_data(build_init_data("123:test"), "123:test", 3600)
    assert payload["id"] == 55


def test_invalid_hash_rejected() -> None:
    with pytest.raises(AppError) as error:
        validate_init_data(build_init_data("123:test") + "x", "123:test", 3600)
    assert error.value.code == "TELEGRAM_AUTH_INVALID"


def test_expired_init_data_rejected() -> None:
    with pytest.raises(AppError) as error:
        validate_init_data(build_init_data("123:test", age=5000), "123:test", 60)
    assert error.value.code == "TELEGRAM_AUTH_EXPIRED"
