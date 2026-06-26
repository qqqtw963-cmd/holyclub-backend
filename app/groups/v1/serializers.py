from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.common.validators import validate_serializer_request_user
from django.utils import timezone

from app.groups.models import Group, GroupInvite, GroupMembership, GroupStatus


class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name", "description", "status"]
        read_only_fields = ["id", "status"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["leader"] = validate_serializer_request_user(self, attrs)
        attrs["status"] = GroupStatus.PENDING
        return attrs


class GroupCreateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "status"]


class GroupMemberSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    name = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        model = GroupMembership
        fields = ["user_id", "name", "role", "joined_at", "is_active"]


class GroupMineSerializer(serializers.ModelSerializer):
    my_role = serializers.CharField(source="membership_role", read_only=True)
    leader_name = serializers.CharField(source="leader.name", read_only=True)

    class Meta:
        model = Group
        fields = ["id", "name", "description", "status", "approved_at", "leader_name", "my_role"]


class GroupDetailSerializer(serializers.ModelSerializer):
    leader_name = serializers.CharField(source="leader.name", read_only=True)
    members = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "name", "description", "status", "approved_at", "leader", "leader_name", "members"]

    def get_members(self, obj):
        memberships = obj.memberships.filter(is_active=True).select_related("user").order_by("joined_at")
        return GroupMemberSerializer(memberships, many=True).data


class GroupInviteCreateSerializer(serializers.ModelSerializer):
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    max_uses = serializers.IntegerField(required=False, allow_null=True, min_value=1)

    class Meta:
        model = GroupInvite
        fields = ["id", "code", "expires_at", "max_uses", "use_count", "created_at"]
        read_only_fields = ["id", "code", "use_count", "created_at"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get("expires_at") is not None and attrs["expires_at"] <= timezone.now():
            raise ValidationError({"expires_at": ["만료일은 현재보다 이후여야 합니다."]})
        attrs["created_by"] = validate_serializer_request_user(self, attrs)
        attrs["group"] = self.context["group"]
        attrs["code"] = GroupInvite.generate_code()
        return attrs


class GroupJoinSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=12)


class GroupJoinResponseSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    membership_id = serializers.IntegerField()
    role = serializers.CharField()
    status = serializers.CharField()


class GroupLeaveResponseSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    is_active = serializers.BooleanField()


class DashboardTodaySerializer(serializers.Serializer):
    prayer_done = serializers.BooleanField()
    word_done = serializers.BooleanField()
    training_done = serializers.BooleanField()
    daily_routine_done = serializers.BooleanField()
    screen_time_minutes = serializers.IntegerField(allow_null=True)


class DashboardWeekSummarySerializer(serializers.Serializer):
    completed_days = serializers.IntegerField()
    total_days = serializers.IntegerField()


class GroupDashboardMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    name = serializers.CharField()
    today = DashboardTodaySerializer()
    week_summary = DashboardWeekSummarySerializer()
    streak = serializers.IntegerField(allow_null=True)


class GroupDashboardGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class GroupDashboardResponseSerializer(serializers.Serializer):
    group = GroupDashboardGroupSerializer()
    members = GroupDashboardMemberSerializer(many=True)
