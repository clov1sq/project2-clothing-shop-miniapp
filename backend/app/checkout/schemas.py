import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

DeliveryMethod = Literal["pickup", "branch", "courier"]


class CheckoutContact(BaseModel):
    first_name: str = Field(min_length=2, max_length=120)
    last_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=9, max_length=32)
    email: str | None = Field(default=None, max_length=255)
    comment: str | None = Field(default=None, max_length=1000)

    @field_validator("first_name", "last_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        cleaned = " ".join(value.strip().split())
        if len(cleaned) < 2:
            raise ValueError("Поле має містити щонайменше 2 символи")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if not value:
            return None
        cleaned = value.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", cleaned):
            raise ValueError("Некоректна email-адреса")
        return cleaned

    @field_validator("comment")
    @classmethod
    def clean_comment(cls, value: str | None) -> str | None:
        cleaned = value.strip() if value else None
        return cleaned or None


class CheckoutDelivery(BaseModel):
    method: DeliveryMethod
    city: str | None = Field(default=None, max_length=160)
    branch: str | None = Field(default=None, max_length=220)
    address: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def validate_method_data(self) -> "CheckoutDelivery":
        self.city = self.city.strip() if self.city else None
        self.branch = self.branch.strip() if self.branch else None
        self.address = self.address.strip() if self.address else None
        if self.method == "branch" and (not self.city or not self.branch):
            raise ValueError("Для доставки у відділення вкажіть місто та відділення")
        if self.method == "courier" and (not self.city or not self.address):
            raise ValueError("Для адресної доставки вкажіть місто та адресу")
        return self


class CheckoutValidateRequest(BaseModel):
    contact: CheckoutContact | None = None
    delivery: CheckoutDelivery | None = None


class CheckoutConfirmRequest(BaseModel):
    contact: CheckoutContact
    delivery: CheckoutDelivery
