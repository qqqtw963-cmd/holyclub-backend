from rest_framework.permissions import IsAuthenticated


class GroupPermission(IsAuthenticated):
    pass
