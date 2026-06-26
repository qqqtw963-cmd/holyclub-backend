import re

from django.contrib.auth.password_validation import (
    CommonPasswordValidator,
    NumericPasswordValidator,
    UserAttributeSimilarityValidator,
)
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ParseError


def get_username_validators():
    validators = [
        ASCIIUsernameValidator(),
        CustomLengthValidator(4, 16),
    ]
    return validators


def validate_username(username):
    validators = get_username_validators()
    errors = []
    for validator in validators:
        try:
            validator.validate(username)
        except ValidationError as error:
            errors.append(error)
    if errors:
        raise ValidationError(errors)


def get_password_validators():
    validators = [
        CustomLengthValidator(8, 16),
        UserAttributeSimilarityValidator(),
        CommonPasswordValidator(),
        NumericPasswordValidator(),
    ]
    return validators


def validate_password(password, password_confirm):
    validators = get_password_validators()

    if password != password_confirm:
        raise ValidationError(
            {
                "password": ["비밀번호와 비밀번호 확인이 일치하지 않습니다."],
                "password_confirm": ["비밀번호와 비밀번호 확인이 일치하지 않습니다."],
            }
        )

    for validator in validators:
        try:
            validator.validate(password)
        except ValidationError as e:
            raise ValidationError({"password": [str(e)]})


def validate_phone_number_length(phone):
    if not bool(re.match("(010|011)[0-9]{7,8}", phone)):
        raise ParseError({"detail": "Invalid phone number format."})


class ASCIIUsernameValidator:
    def __init__(self):
        regex = r"^[\w]+\Z"
        self.p = re.compile(regex, re.ASCII)

    def validate(self, username):
        if not self.p.match(username):
            msg = "영문, 숫자, 밑줄만 가능합니다."
            raise ValidationError(msg)


class CustomLengthValidator:
    def __init__(self, min_length, max_length):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, fields, user=None):
        if len(fields) < self.min_length:
            msg = f"최소 {self.min_length} 문자를 입력해주세요."
            raise ValidationError(msg)
        if len(fields) > self.max_length:
            msg = f"최대 {self.max_length} 문자를 입력해주세요."
            raise ValidationError(msg)
