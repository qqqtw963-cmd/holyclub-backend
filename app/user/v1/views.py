from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer
from rest_framework import mixins, serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from app.user.models import User
from app.user.v1.serializers import (
    UserEmailAuthSerializer,
    UserLogoutSerializer,
    UserPushSettingsSerializer,
    UserRefreshSerializer,
    UserRegisterSerializer,
    UserSerializer,
    UserSocialAuthSerializer,
)
from app.withdrawal_user.models import WithdrawalUser


@extend_schema_view(
    retrieve=extend_schema(
        summary="유저 조회",
        parameters=[
            OpenApiParameter(
                name="local_datetime",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="사용자 디바이스의 현재 시간 (ISO8601 형식, 예: 2024-01-15T14:30:00+09:00)",
            )
        ],
    ),
    update=extend_schema(summary="유저 정보 수정", description="이름, 핸드폰 번호는 수정 불가능"),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(summary="유저 삭제(탈퇴)"),
    swagger_login=extend_schema(exclude=True),
    email_auth=extend_schema(summary="최초 authorization 회원 정보 입력"),
    social_auth=extend_schema(
        summary="유저 소셜 로그인",
        responses={
            200: UserSocialAuthSerializer,
            400: inline_serializer(
                name="UserSocialLoginValidationError",
                fields={
                    "social_token": serializers.CharField(required=False, label="소셜 로그인 토큰"),
                    "non_field": serializers.ListField(required=False, child=serializers.CharField()),
                    "code": serializers.ListField(required=False, child=serializers.CharField()),
                    "state": serializers.ListField(required=False, child=serializers.CharField()),
                },
            ),
        },
    ),
    register=extend_schema(summary="최초 authorization 회원 정보 입력"),
    logout=extend_schema(summary="유저 로그아웃 (사용X)"),
    refresh=extend_schema(summary="유저 리프레시"),
    push_setting=extend_schema(summary="유저 푸시 알림 설정"),
)
class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_value_regex = "me"

    def get_object(self):
        if self.kwargs.get("pk") == "me":
            return self.queryset.select_related("push_user_settings").get(id=self.request.user.id)
        return super().get_object()

    def _create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _save(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=UserEmailAuthSerializer,
        permission_classes=[],
        url_path="auth/email",
    )
    def email_auth(self, request, *args, **kwargs):
        return self._save(request, *args, **kwargs)

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=UserSocialAuthSerializer,
        permission_classes=[],
        url_path="auth/social",
    )
    def social_auth(self, request, *args, **kwargs):
        return self._save(request, *args, **kwargs)

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=UserRegisterSerializer,
        permission_classes=[],
    )
    def register(self, request, *args, **kwargs):
        return self._create(request, *args, **kwargs)

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=UserPushSettingsSerializer,
        permission_classes=[],
    )
    def push_setting(self, request, *args, **kwargs):
        return self._save(request, *args, **kwargs)

    @action(methods=["POST"], detail=False, serializer_class=UserLogoutSerializer)
    def logout(self, request, *args, **kwargs):
        """
        모바일앱에서만 사용하며, 유저와 디바이스 토큰의 연결을 끊어주기위해 사용합니다.
        """
        return self._save(request, *args, **kwargs)

    @action(methods=["POST"], detail=False, serializer_class=UserRefreshSerializer, permission_classes=[])
    def refresh(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        유저 삭제(탈퇴) 시 withdrawal_user에 데이터를 백업한 후 삭제
        """
        instance = self.get_object()

        # withdrawal_user에 데이터 백업
        withdrawal_data = {
            "email": instance.email,
            "name": instance.name,
            "gender": instance.gender,
            "birth_date": instance.birth_date,
            "phone": getattr(instance, "phone", ""),
            "church_name": getattr(instance, "church_name", ""),
            "user_created_at": instance.date_joined,
            "deleted_at": timezone.now(),
        }
        WithdrawalUser.objects.create(**withdrawal_data)

        # 유저 삭제
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
