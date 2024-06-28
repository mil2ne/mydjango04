import ipaddress
from typing import Union, Optional

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models import Expression

from core.forms import fields as core_form_fields


class BooleanYNField(models.BooleanField):
    """Y/N 형태로 데이터베이스에 저장되는 Boolean 필드를 정의"""

    true_value = "Y"
    false_value = "N"

    # BooleanField 디폴트 에러 메시지 재정의
    default_error_messages = {
        # null=False 일 때의 값 오류 메시지
        "invalid": (
            f"“%(value)s” 값은 True/False 값이어야 하며 "
            f"'{true_value}'/'{false_value}' 문자열도 지원합니다."
        ),
        # null=True 일 때의 값 오류 메시지
        "invalid_nullable": (
            f"“%(value)s” 값은 None이거나 True/False 값이어야 하며 "
            f"'{true_value}'/'{false_value}' 문자열도 지원합니다."
        ),
    }

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 1  # 데이터베이스에 1글자로 저장합니다.
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        """쿼리셋 처리 및 데이터베이스 저장은 CharField 타입으로 처리"""
        return "CharField"

    def to_python(self, value: Union[str, bool]) -> Optional[bool]:
        """데이터베이스 값, 폼 입력, 쿼리셋 조회값을 True/False/None 값으로 변환합니다."""

        # nullable일 경우, 빈 값을 전달받으면 None을 반환
        if self.null and value in self.empty_values:
            return None

        # Y/N 문자열만 직접 처리하고,
        if value == self.true_value:
            return True
        if value == self.false_value:
            return False

        # 나머지 값에 대한 변환은 부모인 models.BooleanField에게 넘깁니다.
        return super().to_python(value)

    def from_db_value(
        self,
        value: Optional[str],
        expression: Expression,
        connection: BaseDatabaseWrapper,
    ) -> Optional[bool]:
        """데이터베이스에서 읽어온 값을 True/False/None 값으로 변환합니다."""
        return self.to_python(value)

    def get_prep_value(self, value: Union[str, bool]) -> Optional[str]:
        """SQL 쿼리가 작성될 때 호출됩니다. Y/N/True/False 값을 데이터베이스에 저장할 문자열 Y/N이나 None으로 변환합니다."""
        prep_value: Optional[bool] = super().get_prep_value(
            value
        )  # 내부에서 to_python을 호출하여 값을 변환
        if prep_value is None:
            return None
        return self.true_value if prep_value else self.false_value


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


class DatePickerField(models.DateField):
    def __init__(self, *args, min_value=None, max_value=None, **kwargs):
        self.min_value = min_value
        self.max_value = max_value

        super().__init__(*args, **kwargs)

        if self.min_value is not None:
            self.validators.append(MinValueValidator(self.min_value))

        if self.min_value is not None:
            self.validators.append(MaxValueValidator(self.max_value))

    def formfield(self, **kwargs):
        return super().formfield(
            **kwargs,
            form_class=core_form_fields.DatePickerField,
            min_value=self.min_value,
            max_value=self.max_value,
        )
