import ipaddress
from typing import Union, Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models import Expression


class IPv4AddressIntegerField(models.CharField):
    default_error_messages = {
        "invalid": "“%(value)s” 값은 IPv4 주소나 정수여야 합니다.",
        "invalid_nullable": "“%(value)s” 값은 None이거나 IPv4 주소나 정수여야 합니다.",
    }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 15)
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        """4바이트 unsigned 정수 필드로 매핑"""
        return "PositiveIntegerField"

    def db_type(self, connection):
        if connection.vendor == "postgresql":
            return "bigint"  # 8바이트 정수형
        if connection.vendor == "oracle":
            return "number(19)"  # 8바이트 정수형
        return super().db_type(connection)

    def to_python(self, value: Union[str, int]) -> Optional[str]:
        if self.null and value in self.empty_values:
            return None

        # 정수값을 문자열로 받으면 정수로 변환합니다.
        # IPv4Address에서는 정수 포맷이어도 문자열 타입이면, 문자열 아이피로서 변환을 시도하기 때문입니다.
        if isinstance(value, str) and value.isdigit():
            value = int(value)

        try:
            return str(ipaddress.IPv4Address(value))  # 문자열 아이피로 변환
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            raise ValidationError(
                self.default_error_messages[
                    "invalid_nullable" if self.null else "invalid"
                ],
                code="invalid",
                params={"value": value},
            )

    def from_db_value(
        self,
        value: Optional[int],
        expression: Expression,
        connection: BaseDatabaseWrapper,
    ) -> Optional[str]:
        """데이터베이스에서 읽어온 값을 문자열 아이피나 None으로 변환합니다."""
        return self.to_python(value)

    def get_prep_value(self, value: Union[str, int]) -> Optional[int]:
        """SQL 쿼리가 작성될 때 호출됩니다. 정수/문자열 아이피를 데이터베이스에 저장할 정수나 None으로 변환합니다."""
        prep_value: Optional[str] = super().get_prep_value(value)
        if prep_value is None:
            return None
        return int(ipaddress.IPv4Address(prep_value))
