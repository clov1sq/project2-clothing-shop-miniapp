from pydantic import BaseModel


class TelegramAuthRequest(BaseModel):
    init_data: str = ""


def user_payload(user, role: str | None) -> dict[str, object]:
    return {
        "id": str(user.id),
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "display_name": " ".join(part for part in [user.first_name, user.last_name] if part),
        "role": role,
        "is_admin": role in {"admin", "owner"},
    }
