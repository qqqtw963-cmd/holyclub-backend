import secrets
import string

from django.conf import settings
from django.db import models
from django.utils import timezone


class GroupStatus(models.TextChoices):
    PENDING = "pending", "대기"
    APPROVED = "approved", "승인"
    REJECTED = "rejected", "거절"


class GroupMemberRole(models.TextChoices):
    LEADER = "leader", "방장"
    MEMBER = "member", "팀원"


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="led_groups")
    status = models.CharField(max_length=20, choices=GroupStatus.choices, default=GroupStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "group"
        verbose_name = "그룹"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"


class GroupMembership(models.Model):
    group = models.ForeignKey(Group, related_name="memberships", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="group_memberships")
    role = models.CharField(max_length=10, choices=GroupMemberRole.choices)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "group_membership"
        verbose_name = "그룹 멤버십"
        verbose_name_plural = verbose_name
        ordering = ["-joined_at"]
        unique_together = ("group", "user")

    def __str__(self):
        return f"{self.group_id}-{self.user_id} ({self.role})"


class GroupInvite(models.Model):
    group = models.ForeignKey(Group, related_name="invites", on_delete=models.CASCADE)
    code = models.CharField(max_length=12, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_uses = models.IntegerField(null=True, blank=True)
    use_count = models.IntegerField(default=0)

    class Meta:
        db_table = "group_invite"
        verbose_name = "그룹 초대코드"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.group.name} - {self.code}"

    def is_valid(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        if self.max_uses is not None and self.use_count >= self.max_uses:
            return False
        return True

    @classmethod
    def generate_code(cls, length=8):
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(alphabet) for _ in range(length))
            if not cls.objects.filter(code=code).exists():
                return code
