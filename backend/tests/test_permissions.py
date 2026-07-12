import pytest

from app.auth.dependencies import Identity, require_admin
from app.auth.models import User
from app.core.errors import AppError


async def test_buyer_cannot_access_admin() -> None:
    identity = Identity(user=User(telegram_id=77, first_name="Buyer"), role=None)
    with pytest.raises(AppError) as error:
        await require_admin(identity)
    assert error.value.code == "ADMIN_ACCESS_REQUIRED"
