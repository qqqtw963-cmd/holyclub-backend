import json
import logging

import jwt
import requests
from cryptography.hazmat.primitives import serialization
from django.conf import settings
from django.utils import timezone
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from jwt.algorithms import RSAAlgorithm
from jwt.exceptions import DecodeError, InvalidTokenError
from requests import RequestException
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)
KAKAO_API_TIMEOUT = 10


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
        }
        kakao_client_secret = (settings.KAKAO_CLIENT_SECRET or "").strip()
        if kakao_client_secret and kakao_client_secret != "CHANGE_ME":
            data["client_secret"] = kakao_client_secret
        try:
            response = requests.post(url=url, data=data, timeout=KAKAO_API_TIMEOUT)
        except RequestException as e:
            logger.warning("Kakao token exchange request failed", exc_info=True)
            raise ValidationError("KAKAO GET TOKEN NETWORK ERROR") from e
        if not response.ok:
            logger.warning(
                "Kakao token exchange failed: status=%s body=%s",
                response.status_code,
                response.text[:300],
            )
            raise ValidationError(f"KAKAO GET TOKEN API ERROR: {response.status_code} - {response.text[:300]}")
        data = response.json()

        return data["access_token"]

    def get_social_user_id(self):
        url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {self.get_access_token()}"}
        try:
            response = requests.get(url=url, headers=headers, timeout=KAKAO_API_TIMEOUT)
        except RequestException as e:
            logger.warning("Kakao me request failed", exc_info=True)
            raise ValidationError("KAKAO ME NETWORK ERROR") from e
        if not response.ok:
            logger.warning(
                "Kakao me failed: status=%s body=%s",
                response.status_code,
                response.text[:300],
            )
            if response.status_code == 401:
                raise ValidationError({"non_field": ["카카오 로그인 토큰이 유효하지 않아요. 다시 로그인해 주세요."]})
            raise ValidationError({"non_field": ["카카오 로그인에 실패했어요. 잠시 후 다시 시도해 주세요."]})
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
        try:
            client_secret = jwt.encode(
                payload,
                settings.APPLE_CLIENT_SECRET,
                algorithm="ES256",
                headers=headers,
            )
        except Exception as e:
            logger.warning("Apple client secret generation failed", exc_info=True)
            raise ValidationError("APPLE CLIENT SECRET CONFIG ERROR") from e
        url = "https://appleid.apple.com/auth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.APPLE_CLIENT_ID,
            "client_secret": client_secret,
            "code": self.code,
        }
        try:
            response = requests.post(
                url=url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
        except RequestException as e:
            logger.warning("Apple token exchange request failed", exc_info=True)
            raise ValidationError("APPLE GET TOKEN NETWORK ERROR") from e

        if not response.ok:
            logger.warning(
                "Apple token exchange failed: status=%s body=%s",
                response.status_code,
                response.text[:300],
            )
            raise ValidationError(f"APPLE GET TOKEN API ERROR: {response.status_code} - {response.text[:300]}")

        data = response.json()
        access_token = data["id_token"]
        return access_token

    def get_social_user_id(self):
        access_token = self.get_access_token()

        if not access_token:
            raise ValidationError("APPLE ID TOKEN IS EMPTY")

        try:
            kid = jwt.get_unverified_header(access_token)["kid"]
        except (DecodeError, InvalidTokenError, KeyError) as e:
            raise ValidationError("APPLE ID TOKEN ERROR") from e

        key_payload = requests.get("https://appleid.apple.com/auth/keys", timeout=10).json()
        apple_public_key = RSAAlgorithm.from_jwk(
            json.dumps(next(filter(lambda x: x["kid"] == kid, key_payload["keys"])))
        )
        apple_public_key_as_string = apple_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        try:
            decoded = jwt.decode(
                access_token,
                key=apple_public_key_as_string,
                algorithms=["RS256"],
                audience=[settings.APPLE_APP_ID, settings.APPLE_CLIENT_ID],
            )
        except (DecodeError, InvalidTokenError) as e:
            raise ValidationError("APPLE ID TOKEN ERROR") from e
        return decoded["sub"]


class GoogleAdapter(SocialAdapter):
    key = "google"

    def get_access_token(self):
        if self.access_token:
            return self.access_token

        raise ValidationError("GOOGLE ID TOKEN IS EMPTY")

    def get_social_user_id(self):
        access_token = self.get_access_token()

        if not settings.GOOGLE_CLIENT_IDS:
            raise ValidationError("GOOGLE CLIENT IDS NOT CONFIGURED")

        try:
            decoded = google_id_token.verify_oauth2_token(
                access_token,
                google_requests.Request(),
                audience=None,
            )
        except ValueError as e:
            raise ValidationError("GOOGLE ID TOKEN ERROR") from e

        audience = decoded.get("aud")
        if audience not in settings.GOOGLE_CLIENT_IDS:
            raise ValidationError("GOOGLE ID TOKEN AUDIENCE ERROR")

        social_user_id = decoded.get("sub")
        if not social_user_id:
            raise ValidationError("GOOGLE ID TOKEN SUBJECT ERROR")

        return social_user_id
