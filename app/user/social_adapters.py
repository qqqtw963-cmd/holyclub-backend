import json

import jwt
import requests
from cryptography.hazmat.primitives import serialization
from django.conf import settings
from django.utils import timezone
from jwt.algorithms import RSAAlgorithm
from rest_framework.exceptions import ValidationError


class SocialAdapter:
    key = None

    def __init__(self, code=None, access_token=None, origin=None):
        self.code = code
        self.access_token = access_token
        self.origin = origin

    def get_access_token(self):
        raise NotImplementedError("Not Implemented 'get_access_token' method")

    def get_social_user_id(self):
        raise NotImplementedError("Not Implemented 'get_social_user_id' method")


class KakaoAdapter(SocialAdapter):
    key = "kakao"

    def get_access_token(self):
        if self.access_token:
            return self.access_token

        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": f"{self.origin}{settings.SOCIAL_REDIRECT_PATH}",
            "code": self.code,
            "client_secret": settings.KAKAO_CLIENT_SECRET,
        }
        response = requests.post(url=url, data=data)
        if not response.ok:
            raise ValidationError(f"KAKAO GET TOKEN API ERROR: {response.status_code} - {response.text}")
        data = response.json()

        return data["access_token"]

    def get_social_user_id(self):
        url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {self.get_access_token()}"}
        response = requests.get(url=url, headers=headers)
        if not response.ok:
            raise ValidationError("KAKAO ME API ERROR")
        data = response.json()

        # 카카오 사용자 ID만 반환 (튜플이 아닌 단일 값)
        return data["id"]


class AppleAdapter(SocialAdapter):
    key = "apple"

    def get_access_token(self):
        if self.access_token:
            return self.access_token
        headers = {"kid": settings.APPLE_KEY_ID}
        payload = {
            "iss": settings.APPLE_TEAM_ID,
            "iat": timezone.datetime.now(),
            "exp": timezone.datetime.now() + timezone.timedelta(hours=1),
            "aud": "https://appleid.apple.com",
            "sub": settings.APPLE_CLIENT_ID,
        }
        client_secret = jwt.encode(
            payload,
            settings.APPLE_CLIENT_SECRET,
            algorithm="ES256",
            headers=headers,
        )
        url = "https://appleid.apple.com/auth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.APPLE_CLIENT_ID,
            "client_secret": client_secret,
            "code": self.code,
        }
        response = requests.post(
            url=url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if not response.ok:
            raise ValidationError("APPLE GET TOKEN API ERROR")

        data = response.json()
        access_token = data["id_token"]
        return access_token

    def get_social_user_id(self):
        access_token = self.get_access_token()

        key_payload = requests.get("https://appleid.apple.com/auth/keys").json()
        kid = jwt.get_unverified_header(access_token)["kid"]
        apple_public_key = RSAAlgorithm.from_jwk(
            json.dumps(next(filter(lambda x: x["kid"] == kid, key_payload["keys"])))
        )
        apple_public_key_as_string = apple_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        decoded = jwt.decode(
            access_token,
            key=apple_public_key_as_string,
            algorithms=["RS256"],
            audience=[settings.APPLE_APP_ID, settings.APPLE_CLIENT_ID],
        )
        return decoded["sub"]
